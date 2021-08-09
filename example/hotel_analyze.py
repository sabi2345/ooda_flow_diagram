from ooda_flow_diagram import Diagram, Cluster
from ooda_flow_diagram.ooda.basic import MajorTarget, MajorPrerequisite, Target, Prerequisite,\
    Result, ActCells, ActTable

with Diagram("Hotel Cancellation Prediction", show=True, direction="TB", outformat="svg"):
    with Cluster("Goal"):
        major_precise = MajorPrerequisite(
            label=["Input data is the history of the reservation and cancellation data of xxx hotel group.",
                   "Dead line is 7/23/2021"])

        major_target = MajorTarget(
            label="Binary classification prediction of reservations with high hotel cancellation probability.")

        major_precise - major_target

    with Cluster("First OODA Loop"):
        de_target = Target(label="Select the first and simple features, and binary classify.")
        histgram1 = ActTable(
            todo="check all features' histgrams", bywhen="6/23", who="James", progress="done",
            output="selected 8 features",
            completed_date="6/22")
        bin_classify = ActTable(
            todo="classify with boosting tree model and get first accuracies", bywhen="6/24",
            who="James", progress="done",
            output="accuracies_01.xls",
            completed_date="6/22")
        first_result = Result(label="First accuracy is accuracies_01.xls. That is not enough.")

        major_target >> de_target >> histgram1 >> bin_classify >> first_result

    with Cluster("Second OODA Loop"):
        se_target = Target(label="Merge past reservation information for each user and add user attribute information"
                                 " to the features")
        merge = ActTable(
            todo=["Merge past reservation information for each user"], who="Bell", bywhen="6/28",
            progress="start", output=["data preparation program"], output_mark="seq", todo_mark="point")
        first_result >> se_target >> merge



