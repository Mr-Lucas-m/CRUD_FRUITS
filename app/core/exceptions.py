from fastapi import HTTPException, status


class FruitNotFoundError(HTTPException):
    def __init__(self, fruit_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fruta com id '{fruit_id}' não encontrada.",
        )


class FruitAlreadyExistsError(HTTPException):
    def __init__(self, nome: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma fruta cadastrada com o nome '{nome}'.",
        )
