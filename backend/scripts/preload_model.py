from sentence_transformers import SentenceTransformer
from const.env_variables import EMBEDDING_MODEL_NAME


def main() -> None:
    SentenceTransformer(EMBEDDING_MODEL_NAME)


if __name__ == "__main__":
    main()


