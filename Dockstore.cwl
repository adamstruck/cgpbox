#!/usr/bin/env cwl-runner

class: CommandLineTool
id: "Sanger-CancerGenomeProject-Workflow"
label: "Sanger-CancerGenomeProject-Workflow"

description: |
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
   
dct:creator:
  "@id": "http://sanger.ac.uk/...
  foaf:name: "Keiran Raine"
  foaf:mbox: "mailto:keiranmraine@gmail.com"

requirements:
  - class: ExpressionEngineRequirement
    id: "#node-engine"
    requirements:
    - class: DockerRequirement
      dockerPull: commonworkflowlanguage/nodejs-engine
    engineCommand: cwlNodeEngine.js
  - class: DockerRequirement
    dockerPull: quay.io/repository/wtsicgp/cgp_in_a_box
	- class: ResourceRequirement
		coresMin: 24
		ramMin: 89645.4
		outdirMin: 953674

inputs:
  - id: "#tumor_bam"
    type: File
    inputBinding:
      position: 1
      prefix: "--tumor"
	- id: "#normal_bam"
    type: File
    inputBinding:
      position: 2
      prefix: "--normal"

outputs:
  - id: "#vcf"
    type: array
    items: File
    outputBinding:
      glob: ["*.vcf"]

baseCommand: ["python", "runCgp.py"]
