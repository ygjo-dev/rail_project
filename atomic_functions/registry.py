from dataclasses import dataclass

from planner.execution_plan import ExecutionStep
from planner.conditions import connected

from atomic_functions.connectivity import ConnectivityFunction
from atomic_functions.transfers import TransferFunction


@dataclass
class RoutingDefinition:
    """
    Semantic Router가 선택하는 Workflow Template
    """

    name: str

    prompt_name: str

    execution_plan: list[ExecutionStep]


ROUTING_TABLE = [

    RoutingDefinition(

        name="CONNECTIVITY_WORKFLOW",

        prompt_name="routing/connectivity",

        execution_plan=[

            ExecutionStep(

                executor_cls=ConnectivityFunction,

            ),

        ],

    ),

    RoutingDefinition(

        name="TRANSFER_WORKFLOW",

        prompt_name="routing/transfer",

        execution_plan=[

            ExecutionStep(

                executor_cls=ConnectivityFunction,

            ),

            ExecutionStep(

                executor_cls=TransferFunction,

                condition=connected,

            ),

        ],

    ),

]