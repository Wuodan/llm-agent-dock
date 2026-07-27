from aicage.config.extensions.loader import ExtensionMetadata


def canonical_extensions(
    extensions: list[ExtensionMetadata],
) -> list[ExtensionMetadata]:
    return sorted(
        extensions,
        key=lambda extension: (
            extension.dockerfile_path is not None,
            extension.extension_id,
        ),
    )


def canonical_extension_ids(
    extension_ids: list[str],
    extensions: dict[str, ExtensionMetadata],
) -> list[str]:
    return [
        extension.extension_id
        for extension in canonical_extensions(
            [extensions[extension_id] for extension_id in extension_ids]
        )
    ]
