for run in 1
do
    for cores in single_node_run_8.sh single_node_run_4.sh single_node_run_1.sh
    do
        for index in {1..64}
        do
            sbatch $cores $index $run
        done
    done
done
