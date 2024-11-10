#  Copyright (c) 2024. Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated
#  documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
#  persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pytest

from ColorReliefEditor.config_file import ConfigFile


@pytest.fixture
def valid_yaml_data():
    return """
REGIONS:
  ICELAND:
    FILES:
      A: '*_topo.tif'
      B: 'WESTMAN.tif'
      C: ''
    COMPRESS: --co=COMPRESS=DEFLATE
    CRS1: -t_srs epsg:3857
    CRS2: -r cubic
    CRS3: -overwrite
    EDGE: -compute_edges
    HILLSHADE1: -z 2
    HILLSHADE2: ''
    HILLSHADE3: ''
    HILLSHADE4: ''
    HILLSHADE5: -igor
    LABELS:
      1: ''
      2: ''
      3: ''
      4: ''
      5: ''
    LAYER: B
    LICENSE: CC-BY-4.0  aa
    MERGE1: --extent=intersect --projectionCheck --NoDataValue=none --type=Byte
    MERGE_CALC: (A.astype(float)*B.astype(float))/255.0
    MODE: expert
    PREVIEW: '1000'
    PUBLISH: /Users/mike/iCloudDrive/Documents/Pycharm/map_data/img
    SOURCE_A: https://stac.ecodatacube.eu/dtm_elevation/collection.json
    SOURCE_B: ''
    SOURCE_C: ''
    VIEWER: QGIS
    """


@pytest.fixture
def invalid_yaml_data():
    return """
REGIONS:
  ICELAND:
    CRS1: -t_srs epsg:3857
    CRS2: -r lanczos
    CRS3: -overwrite
unbalanced brackets: ][
    """


@pytest.fixture
def config():
    return ConfigFile()


def test_read_key(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)

    config.load(file_path)
    assert config.region == "ICELAND"
    assert config["CRS1"] == "-t_srs epsg:3857"


def test_read_dot_key(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)

    config.load(file_path)
    assert config["FILES.A"] == '*_topo.tif'


def test_read_indirect(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)

    config.load(file_path)
    assert config.get("FILES.@LAYER") == 'WESTMAN.tif'


def test_read_invalid_yaml(config, invalid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(invalid_yaml_data)

    with pytest.raises(RuntimeError) as exc_info:
        config.load(file_path)

    assert "Failed to parse YAML file" in str(exc_info.value)


def test_read_no_regions(config, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write("REGIONS: {}")

    with pytest.raises(ValueError, match="No regions found in the configuration file."):
        config.load(file_path)


def test_read_no_regions2(config, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write("CONFIG: {}")

    with pytest.raises(ValueError):
        config.load(file_path)


def test_set_and_get_setting(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)

    config.load(file_path)

    config["NEW_KEY"] = "new_value"
    assert config["NEW_KEY"] == "new_value"


def test_set_and_get_multi(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)

    config.load(file_path)

    config["NEW_KEY.A"] = "new_value"
    assert config["NEW_KEY.A"] == "new_value"


def test_set_and_get_indirect(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)
    config.load(file_path)

    config.set("FILES.@LAYER", "value2")
    assert config.get("FILES.@LAYER") == "value2"
    assert config.get("FILES.B") == "value2"


def test_save_valid_yaml(config, valid_yaml_data, tmpdir):
    file_path = tmpdir.join("config.yaml")
    file_path.write(valid_yaml_data)
    config.load(file_path)

    config["CRS1"] = "epsg:4326"
    config.save()

    config.load(file_path)
    assert config["CRS1"] == "epsg:4326"


def test_save_no_data(config, tmpdir):
    with pytest.raises(ValueError):
        config.save()


def test_read_invalid_file_path(config, tmpdir):
    invalid_file_path = tmpdir.join("non_existent_config.yaml")

    with pytest.raises(FileNotFoundError):
        config.load(invalid_file_path)
