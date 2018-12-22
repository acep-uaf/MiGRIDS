#/bin/bash

function expect_file()
{
  if [ ! -f $1 ]; then
    echo "Failure: expected file to exist: $1"
    return 1
  else
    echo "Expected file exists: $1"
    return 0
  fi
}

function expect_dir()
{
  if [ ! -d $1 ]; then
    echo "Expected directory does *not* exist: $1"
    return 1
  else
    echo "Expected directory exists: $1"
    retun 0
  fi
}

function generateRunsSandbox() 
{
  echo "Start: generateRunsSandbox.py"
  python3 ./TestScripts/generateRunsSandbox.py
  if [ $? -ne 0 ]; then
    echo "Error: generateRunsSandbox.py failed - stopping"
    exit 1
  else
    echo "End: generateRunsSandbox.py"
    # expect_dir
    # expect_file
  fi
}

function runSimulationSandbox()
{
  echo "Start: runSimulationSandbox.py"
  python3 ./TestScripts/runSimulationSandbox.py
  if [ $? -ne 0 ]; then
    echo "Error: runSimulationSandbox.py failed - stopping"
    exit 1
  fi
  echo "End: runSimulationSandbox.py"
}

function getRunMetaDataSandbox()
{
  echo "Start: getRunMetaDataSandbox()"
  python3 ./TestScripts/getRunMetaDataSandbox.py
  if [ $? -ne 0 ]; then
    echo "Error: getRunMetaDataSandbox.py failed - stopping"
    exit 1
  fi
  echo "End: getRunMetaDataSandbox()"
}

function plotSetResultSandbox()
{
  echo "Start: plotSetResultSandbox()"
  python3 ./TestScripts/plotSetResultSandbox.py
  if [ $? -ne 0 ]; then
    echo "Error: plotSetResultSandbox.py failed - stopping"
    exit 1
  fi
  echo "End: plotSetResultSandbox()"

}

cd "$(dirname "$0")/.."
export PYTHONPATH=$PYTHONPATH:${PWD}

expected_dirs=(
  MiGRIDSProjects/testProject/OutputData/Set0/Run0/
  MiGRIDSProjects/testProject/OutputData/Set0/Run1/
  MiGRIDSProjects/testProject/OutputData/Set0/Run2/
  MiGRIDSProjects/testProject/OutputData/Set0/Run3/
  MiGRIDSProjects/testProject/OutputData/Set0/Setup/
  MiGRIDSProjects/testProject/OutputData/Set0/figs/
)  

expected_files=(
  MiGRIDSProjects/testProject/OutputData/Set0/eessOverLoadingPdf.pkl
  MiGRIDSProjects/testProject/OutputData/Set0/genOverLoadingPdf.pkl
  MiGRIDSProjects/testProject/OutputData/Set0/set0ComponentAttributes.db
  MiGRIDSProjects/testProject/OutputData/Set0/set0Results.db
  MiGRIDSProjects/testProject/OutputData/Set0/Set0Results.csv
)


if [ "$1" == "--force-clean" ]; then
  FORCE_CLEAN=true
fi

need_clean='false'
echo "checking to make sure we have a clean environment for running test"
for d in ${expected_dirs[@]}; do 
  if [ -d $d ]; then
    if [[ $FORCE_CLEAN ]]; then
      echo "Removing (due to --force-clean): $d"
      rm -rf $d
    else
      echo "Warning: Found directory $d"
      need_clean='true'
    fi
  fi
done

for f in ${expected_files[@]}; do
  if [ -f $f ]; then
    if [[ $FORCE_CLEAN ]]; then
      echo "Removing (due to --force-clean): $f"
      rm $f
    else
      echo "Warning: Found file $f" 
      need_clean='true'
    fi
  fi
done

if [ "$need_clean" == "true" ]; then
  echo "Error: Not running sanity check because previous run data exists"
  echo "Use the --force-clean option to force removal of these files"
  exit 1
fi


generateRunsSandbox
runSimulationSandbox
getRunMetaDataSandbox
plotSetResultSandbox

echo 
echo "----------------------------"
echo "Sanbox scripts completed"
echo 
echo "Checking to make sure we generated expected output"
success='false'
for d in ${expected_dirs[@]}; do 
  if [ ! -d $d ]; then
    echo "Found expected output directory $d"
    success='true'
  fi
done

for f in ${expected_files[@]}; do
  if [ -f $f ]; then
    echo "Found expected output file $f" 
    success='true'
  fi
done

if [ "$success" == "true" ]; then
  echo "sanity check run generated all the expected results"
  echo "browse them in MiGRIDSProjects/testProject/OutputData/"
else
  echo "MiGRIDS sanity check failed"
  exit 1
fi
