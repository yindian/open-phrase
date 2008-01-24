#!/bin/bash

split -l 20 -a 4 <( bzcat ../phrase.txt.bz2 ) phrase.
