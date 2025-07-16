#!/bin/bash
##########################################
#                                        #
#  Specify your SLURM directives         #
#                                        #
##########################################
#
# User's Mail:
#SBATCH --mail-user=d.wolff@unibw.de
#
# When to send mail?:
#SBATCH --mail-type=BEGIN,END,FAIL
#
# Job name:
#SBATCH --job-name=bending-beam-neo-hooke
#
# Output file:
#SBATCH --output=slurm-%j-%x.out
#
# Standard case: specify only number of cpus
#SBATCH --ntasks=1
#
# Walltime: (days-hours:minutes:seconds)
#SBATCH --time=00:30:00
#
# Select respective hardware partion
#SBATCH --partition=all
#
##########################################
#                                        #
#  Advanced SLURM settings	             #
#                                        #
##########################################
#
# If you want to specify a certain number of nodes:
##SBATCH --nodes=2
#
# and exactly 'ntasks-per-node' cpus on each node:
##SBATCH --ntasks-per-node=24
#
# Allocate full node and block for other jobs:
##SBATCH --exclusive
#
# Request specific hardware features:
##SBATCH --constraint="skylake|cascadelake"
#
###########################################

# Setup shell environment and start from home dir
echo $HOME
cd $HOME

source /home/cluster_tools/user/load_four_c_environment.sh

module list
##########################################
#                                        #
#  Specify the paths                     #
#                                        #
##########################################

RUN_FOUR_C="ON"
FOUR_C_BUILD_DIR="$HOME/workspace/build"
EXE="$FOUR_C_BUILD_DIR/4C-release"

CASE_PATH="$HOME/workspace/examples/fem-reference-results/examples/bending_beam/2D/nonlinear_logneohooke"
INPUT="$CASE_PATH/hyperelastic_bending_beam.dat"
FOUR_C_OUTPUT_DIR="$CASE_PATH/"
OUTPUT_PREFIX="output"


##########################################
#                                        #
#  Postprocessing                        #
#                                        #
##########################################

RUN_ENSIGHT_FILTER="OFF"
ENSIGHT_OUTPUT_DIR="$HOME/<pathToEnsightOutputDirectory>"
ENSIGHT_OPTIONS=""


##########################################
#                                        #
#  RESTART SPECIFICATION                 #
#                                        #
##########################################

RESTART_FROM_STEP=0         # specify the restart step here and in .datfile
RESTART_FROM_DIR=""			# same as output
RESTART_FROM_PREFIX="" 		# prefix typically s

#################################################################
# BEGIN ############### DO NOT TOUCH ME #########################
#################################################################

# execute program
source /home/cluster_tools/core/charon_job_core
trap 'EarlyTermination; StageOut' 2 9 15 18
DoChecks
StageIn
RunProgram
wait
StageOut
# show
# END ################## DO NOT TOUCH ME #########################
echo
echo "Job finished with exit code $? at: `date`"
