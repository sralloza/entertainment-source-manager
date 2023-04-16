from app.models.inputs import InMangaInputs, InputsBase, SpyXFamilyInputs, TheTVDBInputs

INPUTS_MAP: dict[str, type[InputsBase]] = {
    "InManga": InMangaInputs,
    "TheTVDB": TheTVDBInputs,
    "SpyXFamily": SpyXFamilyInputs,
}
