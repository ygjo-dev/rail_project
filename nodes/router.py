from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from atomic_functions.registry import ROUTING_TABLE
from state import WorkflowState
from utils.prompt_loader import load_prompt


MODEL = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

SIMILARITY_THRESHOLD = 0.80


CACHE = []

for workflow in ROUTING_TABLE:

    prompt = load_prompt(
        workflow.prompt_name
    )

    embedding = MODEL.encode(
        prompt,
        convert_to_numpy=True,
    )

    CACHE.append(

        {

            "workflow": workflow,

            "embedding": embedding,

        }

    )


def route_state(
    state: WorkflowState,
) -> WorkflowState:

    question_embedding = MODEL.encode(

        state.question,

        convert_to_numpy=True,

    ).reshape(1, -1)

    candidates = []

    for item in CACHE:

        similarity = cosine_similarity(

            question_embedding,

            item["embedding"].reshape(1, -1),

        )[0][0]

        candidates.append(

            {

                "workflow": item["workflow"],

                "name": item["workflow"].name,

                "score": float(similarity),

            }

        )

    candidates.sort(

        key=lambda x: x["score"],

        reverse=True,

    )

    state.routing_candidates = [

        {

            "name": c["name"],

            "score": c["score"],

        }

        for c in candidates

    ]

    if candidates:

        best = candidates[0]

        if best["score"] >= SIMILARITY_THRESHOLD:

            state.execution_plan = (

                best["workflow"]

                .execution_plan

            )

    return state