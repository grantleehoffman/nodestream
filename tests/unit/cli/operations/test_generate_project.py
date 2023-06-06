import pytest
from hamcrest import assert_that, equal_to

from nodestream.cli.operations import GenerateProject


@pytest.fixture
def python_files(project_dir):
    files = ["proj/test1.py", "proj/test2.py", "proj/__init__.py"]
    return [project_dir / file for file in files]


@pytest.fixture
def pipeline_files(project_dir):
    return [project_dir / "pipelines" / "test.yaml"]


@pytest.fixture
def generate_project_command(project_dir, python_files, pipeline_files):
    return GenerateProject(project_dir, pipeline_files, python_files, "neo4j")


def test_generate_project_command_generate_import_directives(
    generate_project_command: GenerateProject,
):
    assert_that(
        generate_project_command.generate_import_directives(),
        equal_to(
            [
                "proj.test1",
                "proj.test2",
                "nodestream.databases.neo4j",
            ]
        ),
    )


def test_generate_pipeline_scope(generate_project_command, pipeline_files, project_dir):
    result = generate_project_command.generate_pipeline_scope()
    assert_that(result.name, equal_to("default"))
    assert_that(
        result.pipelines_by_name["test"].file_path,
        equal_to(pipeline_files[0].relative_to(project_dir)),
    )


@pytest.mark.asyncio
async def test_generate_project_perform(
    generate_project_command, mocker, default_scope
):
    generate_project_command.generate_import_directives = mocker.Mock(
        return_value=["imports"]
    )
    generate_project_command.generate_pipeline_scope = mocker.Mock(
        return_value=default_scope
    )
    result = await generate_project_command.perform(None)
    assert_that(result.imports, equal_to(["imports"]))
    assert_that(result.scopes_by_name, equal_to({"default": default_scope}))
