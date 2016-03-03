#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import os
import re
import subprocess


def collect_args():
    descr = '''
    __cgpbox__ will perform the following analysis (not necessarily in this order):

    * Basic genotype call using the standard Sequenom SNP locations
        * GRCh37 locations [here](https://github.com/cancerit/cgpNgsQc/blob/develop/share/genotype/general.tsv)
    * A comparison of the called genotype between tumour and normal.
    * An evaluation of gender using 4 chrY specific SNPs
        * GRCh37 locations [here](https://github.com/cancerit/cgpNgsQc/blob/develop/share/genotype/gender.tsv)
            * not ordered as first 2 are part of standard Sequenom QCplex, additional are included for improved accuracy in patchy sequencing.
    * Copy Number Variation (CNV) using [ascatNgs](https://github.com/cancerit/ascatNgs)
            * [ASCAT algorithm](https://www.crick.ac.uk/peter-van-loo/software/ASCAT)
    * Insertion and deletion (InDel) calling using [cgpPindel](https://github.com/cancerit/cgpPindel)
            * A variation of [Pindel](http://gmt.genome.wustl.edu/packages/pindel/)
    * Single Nucleotide Variant (SNV) calling using [CaVEMan](https://github.com/cancerit/CaVEMan)
            * Post-processing via [cgpCaVEManPostProcessing](https://github.com/cancerit/cgpCaVEManPostProcessing)
    * Gene annotation of SNV and InDel calls using [VAGrENT](https://github.com/cancerit/VAGrENT)
    * Structural Variation (SV) calls using [BRASS](https://github.com/cancerit/BRASS)
            * Basic gene annotation via [grass](https://github.com/cancerit/grass)
'''
    parser = argparse.ArgumentParser(
        description=descr
    )
    parser.add_argument("--tumor",
                        type=str,
                        required=True,
                        help="patient tumor BAM file")
    parser.add_argument("--normal",
                        type=str,
                        required=True,
                        help="matched normal BAM file")
    parser.add_argument("--pre-processing",
                        nargs='+',
                        type=str,
                        required=False,
                        dest='pre',
                        help="pre-processing commands to run before the workflow")
    parser.add_argument("--post-processing",
                        nargs='+',
                        type=str,
                        required=False,
                        dest='post',
                        help="post-processing commands to run after the workflow")
    return parser


def execute(cmd):
    logging.info("RUNNING: %s" % (cmd))
    print("\nRUNNING...\n", cmd, "\n")
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr is not None:
        print(stderr)
    if stdout is not None:
        print(stdout)
    return p.returncode


def runCgpWorkflow():
    parser = collect_args()
    args = parser.parse_args()

    #############################
    # write params file
    #############################
    params = {"NAME_MT": re.sub('(\.bam|\.bai)', '', os.path.basename(args.tumor)),
              "NAME_WT": re.sub('(\.bam|\.bai)', '', os.path.basename(args.normal)),
              "BAM_MT": os.path.abspath(args.tumor),
              "BAM_WT": os.path.abspath(args.normal)}

    # write header to tmp file
    params_file = os.path.join("/datastore/", "run.params")
    with open(params_file, 'w') as f:
        f.write("#!/bin/bash\n\n")
        # Pre-processing steps
        if args.pre is not None:
            for i in range(len(args.pre)):
                f.write("PRE_EXEC[{0}]={1}\n".format(i, args.pre[i]))
        # Input BAM files
        for key, val in params.items():
            f.write("{0}='{1}'\n".format(key, val))
        # post-processing steps
        if args.post is not None:
            for i in range(len(args.post)):
                f.write("POST_EXEC[{0}]={1}\n".format(i, args.post[i]))
        f.close()

    cmd = "/opt/wtsi-cgp/bin/runCgcp.sh"
    execute(cmd)


if __name__ == "__main__":
    runCgpWorkflow()
