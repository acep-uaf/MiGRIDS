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


generateRunsSandbox
runSimulationSandbox
getRunMetaDataSandbox
plotSetResultSandbox

