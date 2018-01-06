#!/bin/bash
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################

base_dir=$(cd `dirname $0`; pwd)


function auto()
{
    while :
    do
        echo ""
        echo "====================HQ================="
        python main.py
        echo "======================================="
        echo ""
    done
}


# Call sub function.
case C"$1" in
Cauto)
    auto
    ;;
C*)
    echo "Usage: $0 {auto}"
    ;;
esac

rc=$?
exit ${rc}
