from fastapi import HTTPException, status


# ── Fruit ──────────────────────────────────────────────────────────────────────
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


# ── Category ───────────────────────────────────────────────────────────────────
class CategoryNotFoundError(HTTPException):
    def __init__(self, category_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria com id '{category_id}' não encontrada.",
        )


class CategoryAlreadyExistsError(HTTPException):
    def __init__(self, nome: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma categoria cadastrada com o nome '{nome}'.",
        )


class CategoryHasFruitsError(HTTPException):
    def __init__(self, category_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível remover a categoria '{category_id}': existem frutas vinculadas.",
        )


# ── Stock ──────────────────────────────────────────────────────────────────────
class InsufficientStockError(HTTPException):
    def __init__(self, fruit_id: str, solicitado: int, disponivel: int) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Estoque insuficiente para a fruta '{fruit_id}'. "
                f"Solicitado: {solicitado}, disponível: {disponivel}."
            ),
        )


# ── Auth ───────────────────────────────────────────────────────────────────────
class InvalidCredentialsError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class EmailAlreadyRegisteredError(HTTPException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' já está cadastrado.",
        )
