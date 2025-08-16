"""
Test data management system for Unreal MCP tests.

Provides structured test data for different testing scenarios including:
- Actor test data with various configurations
- Blueprint test data with components and properties
- Asset test data for asset management tests
- World/Level test data for level operations
- UMG widget test data for UI testing
- Error condition test data for validation
- Mock response data for offline testing
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

@dataclass
class ActorTestData:
    """Test data for actor-related tests."""
    name: str
    type: str
    location: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    properties: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ComponentTestData:
    """Test data for component-related tests."""
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class BlueprintTestData:
    """Test data for blueprint-related tests."""
    name: str
    parent_class: str
    path: str = "/Game/TestBP"
    components: List[ComponentTestData] = field(default_factory=list)
    variables: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AssetTestData:
    """Test data for asset-related tests."""
    name: str
    type: str
    path: str
    properties: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
@dataclass
class LevelTestData:
    """Test data for level/world-related tests."""
    name: str
    path: str
    actors: List[ActorTestData] = field(default_factory=list)
    lighting_scenario: str = "Default"
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class UMGTestData:
    """Test data for UMG widget tests."""
    widget_name: str
    parent_class: str = "UserWidget"
    path: str = "/Game/UI"
    components: List[Dict[str, Any]] = field(default_factory=list)
    bindings: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

class TestDataManager:
    """Manage test data for various testing scenarios."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__))
        self.data_dir = Path(data_dir)
        self._load_test_data()
        
    def _load_test_data(self):
        """Load test data from JSON files and create structured data."""
        # Basic actor test data
        self.actors = {
            "simple_cube": ActorTestData(
                name="TestCube",
                type="StaticMeshActor",
                location=[0, 0, 100],
                properties={
                    "static_mesh": "/Engine/BasicShapes/Cube.Cube",
                    "mobility": "Static"
                }
            ),
            "movable_sphere": ActorTestData(
                name="TestSphere",
                type="StaticMeshActor",
                location=[200, 0, 100],
                properties={
                    "static_mesh": "/Engine/BasicShapes/Sphere.Sphere",
                    "mobility": "Movable"
                }
            ),
            "light_source": ActorTestData(
                name="TestLight",
                type="PointLight",
                location=[0, 0, 200],
                properties={
                    "intensity": 1000.0,
                    "light_color": [1.0, 1.0, 1.0, 1.0]
                }
            ),
            "player_start": ActorTestData(
                name="TestPlayerStart",
                type="PlayerStart",
                location=[0, 0, 0],
                rotation=[0, 0, 90]
            )
        }
        
        # Blueprint test data
        self.blueprints = {
            "simple_actor": BlueprintTestData(
                name="TestActorBP",
                parent_class="Actor",
                components=[
                    ComponentTestData(
                        type="StaticMeshComponent",
                        name="StaticMesh",
                        properties={"static_mesh": "/Engine/BasicShapes/Cube.Cube"}
                    ),
                    ComponentTestData(
                        type="BoxComponent",
                        name="CollisionBox",
                        properties={"box_extent": [50, 50, 50]}
                    )
                ],
                variables=[
                    {"name": "Health", "type": "float", "default_value": 100.0},
                    {"name": "Speed", "type": "float", "default_value": 300.0}
                ]
            ),
            "pawn_with_input": BlueprintTestData(
                name="TestPawnBP",
                parent_class="Pawn",
                components=[
                    ComponentTestData(
                        type="StaticMeshComponent",
                        name="Mesh",
                        properties={"static_mesh": "/Engine/BasicShapes/Sphere.Sphere"}
                    ),
                    ComponentTestData(
                        type="CameraComponent",
                        name="Camera"
                    ),
                    ComponentTestData(
                        type="FloatingPawnMovement",
                        name="MovementComponent"
                    )
                ],
                variables=[
                    {"name": "MovementSpeed", "type": "float", "default_value": 500.0}
                ]
            ),
            "widget_blueprint": BlueprintTestData(
                name="TestWidgetBP",
                parent_class="UserWidget",
                components=[
                    ComponentTestData(
                        type="TextBlock",
                        name="TitleText",
                        properties={"text": "Test Widget", "font_size": 24}
                    ),
                    ComponentTestData(
                        type="Button",
                        name="ActionButton", 
                        properties={"text": "Click Me"}
                    )
                ]
            )
        }
        
        # Asset test data - Enhanced for comprehensive asset management testing
        self.assets = {
            # Engine assets (always available)
            "engine_cube_mesh": AssetTestData(
                name="Cube",
                type="StaticMesh",
                path="/Engine/BasicShapes/Cube",
                properties={
                    "build_settings": {
                        "build_nanite": False,
                        "build_reversible_index_buffer": True
                    },
                    "collision": {
                        "collision_complexity": "UseComplexAsSimple"
                    }
                },
                dependencies=[]  # Basic mesh has minimal dependencies
            ),
            "engine_sphere_mesh": AssetTestData(
                name="Sphere",
                type="StaticMesh",
                path="/Engine/BasicShapes/Sphere",
                properties={
                    "vertex_count": 382,
                    "triangle_count": 760
                },
                dependencies=[]
            ),
            "engine_cylinder_mesh": AssetTestData(
                name="Cylinder",
                type="StaticMesh",
                path="/Engine/BasicShapes/Cylinder",
                properties={
                    "vertex_count": 96,
                    "triangle_count": 160
                },
                dependencies=[]
            ),
            "engine_plane_mesh": AssetTestData(
                name="Plane",
                type="StaticMesh",
                path="/Engine/BasicShapes/Plane",
                properties={
                    "vertex_count": 4,
                    "triangle_count": 2
                },
                dependencies=[]
            ),
            "engine_default_material": AssetTestData(
                name="DefaultMaterial",
                type="Material",
                path="/Engine/EngineMaterials/DefaultMaterial",
                properties={
                    "shading_model": "DefaultLit",
                    "blend_mode": "Opaque",
                    "two_sided": False
                },
                dependencies=[
                    "/Engine/EngineMaterials/DefaultMaterial_Grid"
                ]
            ),
            "engine_world_grid_material": AssetTestData(
                name="WorldGridMaterial",
                type="Material",
                path="/Engine/EngineMaterials/WorldGridMaterial",
                properties={
                    "shading_model": "DefaultLit",
                    "blend_mode": "Translucent",
                    "two_sided": True
                },
                dependencies=[
                    "/Engine/EngineResources/WhiteSquareTexture",
                    "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture"
                ]
            ),
            
            # Test assets for manipulation
            "test_static_mesh": AssetTestData(
                name="TestMesh",
                type="StaticMesh",
                path="/Game/TestAssets/TestMesh",
                properties={
                    "build_settings": {
                        "build_nanite": False,
                        "build_reversible_index_buffer": True
                    }
                },
                dependencies=[
                    "/Engine/BasicShapes/Cube"  # Based on cube
                ]
            ),
            "test_material": AssetTestData(
                name="TestMaterial",
                type="Material",
                path="/Game/TestAssets/TestMaterial",
                properties={
                    "shading_model": "DefaultLit",
                    "blend_mode": "Opaque",
                    "metallic": 0.5,
                    "roughness": 0.8
                },
                dependencies=[
                    "/Engine/EngineMaterials/DefaultMaterial"
                ]
            ),
            "test_texture": AssetTestData(
                name="TestTexture",
                type="Texture2D", 
                path="/Game/TestAssets/TestTexture",
                properties={
                    "compression_settings": "TC_Default",
                    "texture_group": "TEXTUREGROUP_World",
                    "size_x": 512,
                    "size_y": 512,
                    "format": "PF_DXT5"
                },
                dependencies=[]
            ),
            "test_blueprint": AssetTestData(
                name="TestBlueprint",
                type="Blueprint",
                path="/Game/TestAssets/TestBlueprint",
                properties={
                    "parent_class": "Actor",
                    "blueprint_type": "BPTYPE_Normal"
                },
                dependencies=[
                    "/Game/TestAssets/TestMesh",
                    "/Game/TestAssets/TestMaterial"
                ]
            ),
            
            # Assets for duplication testing
            "duplicate_source": AssetTestData(
                name="SourceAsset",
                type="StaticMesh",
                path="/Game/TestAssets/SourceAsset",
                properties={},
                dependencies=["/Engine/BasicShapes/Sphere"]
            ),
            "duplicate_target": AssetTestData(
                name="DuplicatedAsset",
                type="StaticMesh",
                path="/Game/TestAssets/DuplicatedAsset",
                properties={},
                dependencies=["/Engine/BasicShapes/Sphere"]
            ),
            
            # Assets for rename testing
            "rename_source": AssetTestData(
                name="AssetToRename",
                type="Material",
                path="/Game/TestAssets/AssetToRename",
                properties={
                    "shading_model": "DefaultLit"
                },
                dependencies=[]
            ),
            "rename_target": AssetTestData(
                name="RenamedAsset",
                type="Material",
                path="/Game/TestAssets/RenamedAsset",
                properties={
                    "shading_model": "DefaultLit"
                },
                dependencies=[]
            ),
            
            # Assets for move testing
            "move_source": AssetTestData(
                name="AssetToMove",
                type="Texture2D",
                path="/Game/TestAssets/AssetToMove",
                properties={
                    "compression_settings": "TC_Default"
                },
                dependencies=[]
            ),
            "move_target": AssetTestData(
                name="MovedAsset", 
                type="Texture2D",
                path="/Game/TestAssets/Moved/MovedAsset",
                properties={
                    "compression_settings": "TC_Default"
                },
                dependencies=[]
            )
        }
        
        # Asset search test data
        self.asset_search_data = {
            "search_terms": {
                "cube_variants": ["cube", "Cube", "CUBE", "cUbE"],
                "sphere_variants": ["sphere", "Sphere", "SPHERE", "sPhErE"],
                "material_variants": ["material", "Material", "MATERIAL"],
                "partial_matches": ["Cub", "Sph", "Mat", "Def"],
                "common_names": ["Default", "World", "Grid", "Engine"],
                "special_chars": ["*", "?", "[", "]", "\\", "/", ".", "-", "_"],
                "empty_search": "",
                "nonexistent": "NonExistentAssetNameXYZ123"
            },
            "expected_results": {
                "cube_search": {
                    "min_results": 1,
                    "should_contain": ["/Engine/BasicShapes/Cube"],
                    "result_patterns": ["cube", "Cube"]
                },
                "material_search": {
                    "min_results": 1,
                    "should_contain": ["/Engine/EngineMaterials/DefaultMaterial"],
                    "result_patterns": ["material", "Material"]
                }
            }
        }
        
        # Asset metadata test expectations
        self.asset_metadata_expectations = {
            "/Engine/BasicShapes/Cube": {
                "required_fields": ["path", "type", "name"],
                "expected_type": "StaticMesh",
                "path_should_contain": "Cube"
            },
            "/Engine/EngineMaterials/DefaultMaterial": {
                "required_fields": ["path", "type", "name"],
                "expected_type": "Material",
                "path_should_contain": "Material"
            }
        }
        
        # Asset registry test data  
        self.asset_registry_data = {
            "reference_test_assets": {
                # Assets that are commonly referenced
                "default_material": {
                    "path": "/Engine/EngineMaterials/DefaultMaterial",
                    "expected_reference_count_min": 0,
                    "commonly_referenced_by": ["materials", "meshes", "blueprints"]
                },
                "basic_shapes": {
                    "paths": [
                        "/Engine/BasicShapes/Cube",
                        "/Engine/BasicShapes/Sphere",
                        "/Engine/BasicShapes/Cylinder"
                    ],
                    "expected_reference_count_min": 0,
                    "commonly_referenced_by": ["blueprints", "actors"]
                }
            },
            "dependency_test_assets": {
                "simple_mesh": {
                    "path": "/Engine/BasicShapes/Cube",
                    "expected_dependency_count_max": 5,  # Basic meshes have few dependencies
                    "common_dependencies": ["materials", "textures"]
                },
                "complex_material": {
                    "path": "/Engine/EngineMaterials/WorldGridMaterial",
                    "expected_dependency_count_min": 1,  # Materials usually have dependencies
                    "common_dependencies": ["textures", "functions", "parameters"]
                }
            }
        }
        
        # Level test data - Enhanced for comprehensive world/level testing
        self.levels = {
            "basic_test_level": LevelTestData(
                name="TestLevel",
                path="/Game/TestLevels/TestLevel",
                actors=[
                    self.actors["simple_cube"],
                    self.actors["movable_sphere"],
                    self.actors["light_source"],
                    self.actors["player_start"]
                ],
                lighting_scenario="MovableDirectionalLight",
                properties={
                    "world_composition": False,
                    "enable_streaming": True,
                    "default_lighting": True
                }
            ),
            "empty_test_level": LevelTestData(
                name="EmptyTestLevel",
                path="/Game/TestLevels/EmptyTestLevel",
                actors=[],
                lighting_scenario="None",
                properties={
                    "world_composition": False,
                    "enable_streaming": False,
                    "default_lighting": False
                }
            ),
            "complex_test_level": LevelTestData(
                name="ComplexTestLevel",
                path="/Game/TestLevels/ComplexTestLevel",
                actors=[
                    self.actors["simple_cube"],
                    self.actors["movable_sphere"],
                    self.actors["light_source"],
                    self.actors["player_start"]
                ],
                lighting_scenario="StationaryDirectionalLight",
                properties={
                    "world_composition": True,
                    "enable_streaming": True,
                    "has_landscapes": True,
                    "streaming_level_count": 3
                }
            ),
            "streaming_main_level": LevelTestData(
                name="StreamingMainLevel",
                path="/Game/StreamingLevels/MainLevel",
                actors=[self.actors["player_start"]],
                lighting_scenario="StationaryDirectionalLight",
                properties={
                    "world_composition": True,
                    "enable_streaming": True,
                    "is_persistent": True,
                    "streaming_levels": [
                        "/Game/StreamingLevels/AudioLevel",
                        "/Game/StreamingLevels/GeometryLevel",
                        "/Game/StreamingLevels/LightingLevel"
                    ]
                }
            ),
            "audio_streaming_level": LevelTestData(
                name="AudioLevel",
                path="/Game/StreamingLevels/AudioLevel",
                actors=[],
                lighting_scenario="None",
                properties={
                    "is_streaming_level": True,
                    "streaming_method": "always_loaded",
                    "audio_only": True
                }
            ),
            "geometry_streaming_level": LevelTestData(
                name="GeometryLevel", 
                path="/Game/StreamingLevels/GeometryLevel",
                actors=[self.actors["simple_cube"], self.actors["movable_sphere"]],
                lighting_scenario="None",
                properties={
                    "is_streaming_level": True,
                    "streaming_method": "distance_based",
                    "streaming_distance": 5000.0,
                    "has_geometry": True
                }
            ),
            "lighting_streaming_level": LevelTestData(
                name="LightingLevel",
                path="/Game/StreamingLevels/LightingLevel", 
                actors=[self.actors["light_source"]],
                lighting_scenario="StationaryDirectionalLight",
                properties={
                    "is_streaming_level": True,
                    "streaming_method": "blueprint_controlled",
                    "lighting_only": True
                }
            ),
            "performance_test_level": LevelTestData(
                name="PerformanceTestLevel",
                path="/Game/TestLevels/PerformanceTestLevel",
                actors=[self.actors["simple_cube"]] * 10,  # Multiple instances for testing
                lighting_scenario="StaticDirectionalLight",
                properties={
                    "optimized_for_performance": True,
                    "large_actor_count": True,
                    "test_level": True
                }
            )
        }
        
        # Landscape test data - Enhanced for comprehensive landscape testing
        self.landscapes = {
            "small_test_landscape": {
                "name": "SmallTestLandscape",
                "size_x": 63,
                "size_y": 63,
                "sections_per_component": 1,
                "quads_per_section": 31,
                "location": [0.0, 0.0, 0.0],
                "properties": {
                    "material": "/Game/Materials/LandscapeMaterial",
                    "layers": ["Grass", "Dirt"],
                    "heightmap_resolution": 64,
                    "collision_enabled": True
                }
            },
            "medium_test_landscape": {
                "name": "MediumTestLandscape", 
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 1,
                "quads_per_section": 63,
                "location": [5000.0, 0.0, 0.0],
                "properties": {
                    "material": "/Game/Materials/LandscapeMaterial",
                    "layers": ["Grass", "Dirt", "Rock"],
                    "heightmap_resolution": 128,
                    "collision_enabled": True,
                    "lod_distances": [0, 1000, 2000, 4000]
                }
            },
            "large_test_landscape": {
                "name": "LargeTestLandscape",
                "size_x": 255,
                "size_y": 255,
                "sections_per_component": 2,
                "quads_per_section": 63,
                "location": [10000.0, 0.0, 0.0],
                "properties": {
                    "material": "/Game/Materials/LandscapeMaterial",
                    "layers": ["Grass", "Dirt", "Rock", "Sand"],
                    "heightmap_resolution": 256,
                    "collision_enabled": True,
                    "lod_distances": [0, 2000, 4000, 8000, 16000],
                    "use_nanite": False,
                    "streaming_enabled": True
                }
            },
            "elevated_test_landscape": {
                "name": "ElevatedTestLandscape",
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 1,
                "quads_per_section": 63,
                "location": [0.0, 0.0, 1000.0],
                "properties": {
                    "material": "/Game/Materials/ElevatedLandscapeMaterial",
                    "layers": ["Rock", "Snow"],
                    "heightmap_resolution": 128,
                    "collision_enabled": True,
                    "elevated": True
                }
            },
            "multi_component_landscape": {
                "name": "MultiComponentLandscape",
                "size_x": 127,
                "size_y": 127,
                "sections_per_component": 4,
                "quads_per_section": 31,
                "location": [15000.0, 0.0, 0.0],
                "properties": {
                    "material": "/Game/Materials/LandscapeMaterial",
                    "layers": ["Grass", "Dirt", "Rock"],
                    "heightmap_resolution": 128,
                    "collision_enabled": True,
                    "high_component_count": True,
                    "optimized_for_detail": True
                }
            }
        }
        
        # World/Level operation test data
        self.world_operations = {
            "level_creation": {
                "test_levels": [
                    {"name": "BasicCreationTest", "template": "Default"},
                    {"name": "EmptyCreationTest", "template": "Empty"},
                    {"name": "MinimalCreationTest", "template": "Minimal"},
                    {"name": "VRCreationTest", "template": "VR-Basic"}
                ],
                "expected_actors": {
                    "Default": ["WorldSettings", "PostProcessVolume"],
                    "Empty": ["WorldSettings"],
                    "Minimal": ["WorldSettings"],
                    "VR-Basic": ["WorldSettings", "PostProcessVolume", "PlayerStart"]
                }
            },
            "streaming_levels": {
                "main_level": "/Game/StreamingTest/MainLevel",
                "streaming_levels": [
                    {
                        "name": "Audio",
                        "path": "/Game/StreamingTest/AudioLevel",
                        "method": "always_loaded",
                        "location": [0, 0, 0]
                    },
                    {
                        "name": "Geometry", 
                        "path": "/Game/StreamingTest/GeometryLevel",
                        "method": "distance_based",
                        "location": [2000, 0, 0],
                        "distance": 5000
                    },
                    {
                        "name": "Lighting",
                        "path": "/Game/StreamingTest/LightingLevel", 
                        "method": "blueprint_controlled",
                        "location": [0, 2000, 0]
                    }
                ]
            },
            "landscape_operations": {
                "modification_types": [
                    "sculpt", "smooth", "flatten", "ramp", "erosion", 
                    "hydro_erosion", "noise", "retopologize"
                ],
                "paint_layers": [
                    {"name": "Grass", "weight": 1.0, "color": [0, 1, 0, 1]},
                    {"name": "Dirt", "weight": 0.8, "color": [0.5, 0.3, 0.1, 1]},
                    {"name": "Rock", "weight": 0.6, "color": [0.4, 0.4, 0.4, 1]},
                    {"name": "Sand", "weight": 0.4, "color": [1, 1, 0.5, 1]},
                    {"name": "Snow", "weight": 0.3, "color": [1, 1, 1, 1]},
                    {"name": "Water", "weight": 0.2, "color": [0, 0.5, 1, 1]}
                ],
                "brush_settings": {
                    "small": {"size": 100, "strength": 0.5, "falloff": 0.5},
                    "medium": {"size": 500, "strength": 0.7, "falloff": 0.4},
                    "large": {"size": 1000, "strength": 1.0, "falloff": 0.3}
                }
            }
        }
        
        # UMG widget test data
        self.widgets = {
            "main_menu": UMGTestData(
                widget_name="MainMenuWidget",
                components=[
                    {
                        "type": "TextBlock",
                        "name": "TitleText",
                        "text": "Main Menu",
                        "position": [400, 100],
                        "size": [200, 50],
                        "font_size": 24
                    },
                    {
                        "type": "Button",
                        "name": "StartButton",
                        "text": "Start Game",
                        "position": [350, 200],
                        "size": [100, 40]
                    },
                    {
                        "type": "Button", 
                        "name": "QuitButton",
                        "text": "Quit",
                        "position": [350, 250],
                        "size": [100, 40]
                    }
                ],
                events=[
                    {
                        "widget": "StartButton",
                        "event": "OnClicked",
                        "function": "StartGame"
                    },
                    {
                        "widget": "QuitButton",
                        "event": "OnClicked", 
                        "function": "QuitGame"
                    }
                ]
            ),
            "hud_widget": UMGTestData(
                widget_name="HUDWidget",
                components=[
                    {
                        "type": "TextBlock",
                        "name": "HealthText",
                        "text": "Health: 100",
                        "position": [20, 20],
                        "size": [150, 30]
                    },
                    {
                        "type": "ProgressBar",
                        "name": "HealthBar",
                        "position": [20, 50],
                        "size": [200, 20],
                        "percent": 1.0
                    }
                ],
                bindings=[
                    {
                        "widget": "HealthText",
                        "property": "Text",
                        "binding": "GetHealthText"
                    },
                    {
                        "widget": "HealthBar",
                        "property": "Percent",
                        "binding": "GetHealthPercent"
                    }
                ]
            )
        }
        
    def get_actor_data(self, key: str) -> ActorTestData:
        """Get actor test data by key."""
        return self.actors.get(key)
        
    def get_blueprint_data(self, key: str) -> BlueprintTestData:
        """Get blueprint test data by key."""
        return self.blueprints.get(key)
        
    def get_asset_data(self, key: str) -> AssetTestData:
        """Get asset test data by key."""
        return self.assets.get(key)
        
    def get_level_data(self, key: str) -> LevelTestData:
        """Get level test data by key."""
        return self.levels.get(key)
        
    def get_widget_data(self, key: str) -> UMGTestData:
        """Get UMG widget test data by key."""
        return self.widgets.get(key)
    
    def get_landscape_data(self, key: str) -> Dict[str, Any]:
        """Get landscape test data by key.""" 
        return self.landscapes.get(key, {})
    
    def get_world_operations_data(self) -> Dict[str, Any]:
        """Get world/level operations test data."""
        return self.world_operations
    
    def get_level_creation_data(self) -> Dict[str, Any]:
        """Get level creation test data."""
        return self.world_operations.get("level_creation", {})
    
    def get_streaming_levels_data(self) -> Dict[str, Any]:
        """Get streaming levels test data."""
        return self.world_operations.get("streaming_levels", {})
    
    def get_landscape_operations_data(self) -> Dict[str, Any]:
        """Get landscape operations test data."""
        return self.world_operations.get("landscape_operations", {})
    
    def get_asset_search_data(self) -> Dict[str, Any]:
        """Get asset search test data."""
        return self.asset_search_data
    
    def get_asset_metadata_expectations(self) -> Dict[str, Any]:
        """Get asset metadata test expectations."""
        return self.asset_metadata_expectations
    
    def get_asset_registry_data(self) -> Dict[str, Any]:
        """Get asset registry test data."""
        return self.asset_registry_data
    
    def get_engine_assets(self) -> Dict[str, AssetTestData]:
        """Get all Engine assets for testing."""
        return {k: v for k, v in self.assets.items() if k.startswith("engine_")}
    
    def get_test_assets(self) -> Dict[str, AssetTestData]:
        """Get all test assets (non-Engine) for testing.""" 
        return {k: v for k, v in self.assets.items() if not k.startswith("engine_")}
    
    def get_assets_by_type(self, asset_type: str) -> Dict[str, AssetTestData]:
        """Get assets filtered by type."""
        return {k: v for k, v in self.assets.items() if v.type.lower() == asset_type.lower()}
    
    def get_assets_for_manipulation_tests(self) -> Dict[str, AssetTestData]:
        """Get assets designed for manipulation testing (duplicate, rename, move, etc.)."""
        manipulation_keys = [
            "duplicate_source", "duplicate_target",
            "rename_source", "rename_target", 
            "move_source", "move_target",
            "test_static_mesh", "test_material", "test_texture"
        ]
        return {k: self.assets[k] for k in manipulation_keys if k in self.assets}
        
    def get_mock_responses(self) -> Dict[str, Dict[str, Any]]:
        """Get mock response data for offline testing."""
        return {
            # Editor commands
            "get_actors_in_level": {
                "success": True,
                "result": [
                    {
                        "name": "TestCube",
                        "type": "StaticMeshActor",
                        "location": [0, 0, 100],
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1]
                    },
                    {
                        "name": "TestSphere",
                        "type": "StaticMeshActor", 
                        "location": [200, 0, 100],
                        "rotation": [0, 0, 0],
                        "scale": [1, 1, 1]
                    }
                ]
            },
            "spawn_actor": {
                "success": True,
                "result": "Actor spawned successfully"
            },
            "delete_actor": {
                "success": True,
                "result": "Actor deleted successfully"
            },
            "set_actor_transform": {
                "success": True,
                "result": "Transform updated successfully"
            },
            
            # Blueprint commands
            "create_blueprint": {
                "success": True,
                "result": "Blueprint created successfully"
            },
            "compile_blueprint": {
                "success": True,
                "result": "Blueprint compiled successfully"
            },
            "add_component_to_blueprint": {
                "success": True,
                "result": "Component added successfully"
            },
            "spawn_blueprint_actor": {
                "success": True,
                "result": "Blueprint actor spawned successfully"
            },
            
            # Asset commands - Enhanced for comprehensive testing
            "load_asset": {
                "success": True,
                "result": {
                    "message": "Asset loaded successfully",
                    "asset_path": "/Engine/BasicShapes/Cube",
                    "load_time": 0.05
                }
            },
            "save_asset": {
                "success": True,
                "result": {
                    "message": "Asset saved successfully",
                    "asset_path": "/Game/TestAssets/TestAsset",
                    "save_time": 0.12
                }
            },
            "duplicate_asset": {
                "success": True,
                "result": {
                    "message": "Asset duplicated successfully",
                    "source_path": "/Engine/BasicShapes/Cube",
                    "destination_path": "/Game/TestAssets/DuplicatedCube"
                }
            },
            "delete_asset": {
                "success": True,
                "result": {
                    "message": "Asset deleted successfully",
                    "asset_path": "/Game/TestAssets/AssetToDelete"
                }
            },
            "rename_asset": {
                "success": True,
                "result": {
                    "message": "Asset renamed successfully",
                    "old_path": "/Game/TestAssets/OldName",
                    "new_path": "/Game/TestAssets/NewName"
                }
            },
            "move_asset": {
                "success": True,
                "result": {
                    "message": "Asset moved successfully",
                    "source_path": "/Game/TestAssets/SourceLocation",
                    "destination_path": "/Game/TestAssets/NewLocation/Asset"
                }
            },
            "import_asset": {
                "success": True,
                "result": {
                    "message": "Asset imported successfully",
                    "file_path": "/path/to/file.fbx",
                    "imported_asset_path": "/Game/TestAssets/ImportedAsset",
                    "import_time": 2.5
                }
            },
            "export_asset": {
                "success": True,
                "result": {
                    "message": "Asset exported successfully",
                    "asset_path": "/Game/TestAssets/AssetToExport",
                    "export_path": "/path/to/export/location.fbx",
                    "export_time": 1.8
                }
            },
            
            # Content browser commands
            "list_assets": {
                "success": True,
                "result": [
                    {
                        "name": "Cube",
                        "path": "/Engine/BasicShapes/Cube",
                        "type": "StaticMesh",
                        "size": "1024 KB"
                    },
                    {
                        "name": "Sphere",
                        "path": "/Engine/BasicShapes/Sphere", 
                        "type": "StaticMesh",
                        "size": "2048 KB"
                    },
                    {
                        "name": "DefaultMaterial",
                        "path": "/Engine/EngineMaterials/DefaultMaterial",
                        "type": "Material",
                        "size": "512 KB"
                    }
                ]
            },
            "get_asset_metadata": {
                "success": True,
                "result": {
                    "path": "/Engine/BasicShapes/Cube",
                    "name": "Cube",
                    "type": "StaticMesh",
                    "size": "1024 KB",
                    "vertex_count": 8,
                    "triangle_count": 12,
                    "created_date": "2024-01-01T00:00:00Z",
                    "modified_date": "2024-01-01T00:00:00Z",
                    "tags": ["BasicShape", "Primitive", "Geometry"],
                    "properties": {
                        "collision_complexity": "UseComplexAsSimple",
                        "build_settings": {
                            "build_nanite": False,
                            "build_reversible_index_buffer": True
                        }
                    }
                }
            },
            "search_assets": {
                "success": True,
                "result": [
                    {
                        "name": "Cube",
                        "path": "/Engine/BasicShapes/Cube",
                        "type": "StaticMesh",
                        "relevance_score": 1.0
                    },
                    {
                        "name": "CubeMaterial",
                        "path": "/Game/Materials/CubeMaterial",
                        "type": "Material",
                        "relevance_score": 0.8
                    }
                ]
            },
            
            # Asset registry commands
            "get_asset_references": {
                "success": True,
                "result": [
                    {
                        "path": "/Game/Blueprints/TestActor",
                        "type": "Blueprint",
                        "reference_type": "hard_reference"
                    },
                    {
                        "path": "/Game/Materials/CubeMaterial",
                        "type": "Material",
                        "reference_type": "soft_reference"
                    }
                ]
            },
            "get_asset_dependencies": {
                "success": True,
                "result": [
                    {
                        "path": "/Engine/EngineMaterials/DefaultMaterial",
                        "type": "Material",
                        "dependency_type": "default_material"
                    },
                    {
                        "path": "/Engine/EngineResources/DefaultTexture",
                        "type": "Texture2D",
                        "dependency_type": "texture_reference"
                    }
                ]
            },
            "find_asset": {
                "success": True,
                "result": {
                    "name": "TestAsset",
                    "path": "/Game/TestAssets/TestAsset",
                    "type": "StaticMesh"
                }
            },
            
            # Level Editor commands - Enhanced for comprehensive testing
            "create_level": {
                "success": True,
                "result": {
                    "message": "Level created successfully",
                    "level_name": "TestLevel",
                    "level_path": "/Game/TestLevel",
                    "template_used": "Default",
                    "creation_time": 3.2,
                    "default_actors": ["WorldSettings", "PostProcessVolume"]
                }
            },
            "save_level": {
                "success": True,
                "result": {
                    "message": "Level saved successfully",
                    "level_path": "/Game/TestLevel",
                    "save_time": 1.5,
                    "file_size": "2.4 MB",
                    "actors_saved": 12
                }
            },
            "load_level": {
                "success": True,
                "result": {
                    "message": "Level loaded successfully", 
                    "level_path": "/Game/TestLevel",
                    "load_time": 2.8,
                    "actors_loaded": 12,
                    "streaming_levels_loaded": 2
                }
            },
            "set_level_visibility": {
                "success": True,
                "result": {
                    "message": "Level visibility updated",
                    "level_name": "TestLevel",
                    "visible": True,
                    "affects_streaming": False
                }
            },
            "create_streaming_level": {
                "success": True,
                "result": {
                    "message": "Streaming level created successfully",
                    "level_path": "/Game/StreamingLevels/TestStreamingLevel",
                    "streaming_method": "distance_based",
                    "location": [0, 0, 0],
                    "bounds": {
                        "min": [-1000, -1000, -1000],
                        "max": [1000, 1000, 1000]
                    }
                }
            },
            "load_streaming_level": {
                "success": True,
                "result": {
                    "message": "Streaming level loaded successfully",
                    "level_name": "TestStreamingLevel",
                    "load_time": 1.2,
                    "actors_loaded": 8,
                    "memory_usage": "1.8 MB"
                }
            },
            "unload_streaming_level": {
                "success": True,
                "result": {
                    "message": "Streaming level unloaded successfully",
                    "level_name": "TestStreamingLevel",
                    "unload_time": 0.5,
                    "memory_freed": "1.8 MB"
                }
            },
            
            # Landscape commands - Enhanced for comprehensive testing
            "create_landscape": {
                "success": True,
                "result": {
                    "message": "Landscape created successfully",
                    "landscape_id": "Landscape_1",
                    "size": [127, 127],
                    "location": [0, 0, 0],
                    "sections_per_component": 1,
                    "quads_per_section": 63,
                    "total_components": 4,
                    "heightmap_resolution": 128,
                    "creation_time": 5.7
                }
            },
            "modify_landscape": {
                "success": True,
                "result": {
                    "message": "Landscape modified successfully",
                    "modification_type": "sculpt",
                    "affected_area": {
                        "center": [0, 0],
                        "radius": 500
                    },
                    "vertices_modified": 1024,
                    "operation_time": 0.3
                }
            },
            "paint_landscape_layer": {
                "success": True,
                "result": {
                    "message": "Landscape layer painted successfully",
                    "layer_name": "Grass",
                    "paint_strength": 1.0,
                    "affected_area": {
                        "center": [0, 0],
                        "radius": 300
                    },
                    "vertices_painted": 512,
                    "operation_time": 0.2
                }
            },
            "get_landscape_info": {
                "success": True,
                "result": {
                    "landscapes": [
                        {
                            "landscape_id": "Landscape_1",
                            "name": "TestLandscape",
                            "size_x": 127,
                            "size_y": 127,
                            "location": [0, 0, 0],
                            "sections_per_component": 1,
                            "quads_per_section": 63,
                            "total_components": 4,
                            "heightmap_resolution": 128,
                            "material": "/Game/Materials/LandscapeMaterial",
                            "layers": [
                                {
                                    "name": "Grass",
                                    "weight": 0.8,
                                    "texture": "/Game/Textures/GrassTexture"
                                },
                                {
                                    "name": "Dirt", 
                                    "weight": 0.4,
                                    "texture": "/Game/Textures/DirtTexture"
                                }
                            ],
                            "bounds": {
                                "min": [-8128, -8128, -1000],
                                "max": [8128, 8128, 1000]
                            },
                            "collision_enabled": True,
                            "lod_distances": [0, 1000, 2000, 4000]
                        }
                    ],
                    "total_count": 1,
                    "query_time": 0.1
                }
            },
            
            # World Runtime commands - Enhanced for comprehensive testing
            "get_current_level_info": {
                "success": True,
                "result": {
                    "level_name": "TestLevel",
                    "level_path": "/Game/TestLevel", 
                    "world_name": "TestWorld",
                    "is_persistent": True,
                    "is_visible": True,
                    "world_composition_enabled": False,
                    "streaming_enabled": True,
                    "actors": [
                        {
                            "name": "WorldSettings",
                            "type": "WorldSettings",
                            "location": [0, 0, 0],
                            "is_editor_only": False
                        },
                        {
                            "name": "PostProcessVolume",
                            "type": "PostProcessVolume", 
                            "location": [0, 0, 0],
                            "is_editor_only": False,
                            "unbound": True
                        },
                        {
                            "name": "DirectionalLight",
                            "type": "DirectionalLight",
                            "location": [0, 0, 300],
                            "rotation": [0, -45, 0],
                            "mobility": "Stationary"
                        }
                    ],
                    "streaming_levels": [
                        {
                            "name": "AudioLevel",
                            "path": "/Game/StreamingLevels/AudioLevel",
                            "is_loaded": True,
                            "is_visible": True,
                            "streaming_method": "always_loaded"
                        },
                        {
                            "name": "GeometryLevel",
                            "path": "/Game/StreamingLevels/GeometryLevel", 
                            "is_loaded": False,
                            "is_visible": False,
                            "streaming_method": "distance_based",
                            "streaming_distance": 5000
                        }
                    ],
                    "landscapes": [
                        {
                            "landscape_id": "Landscape_1",
                            "size": [127, 127],
                            "location": [0, 0, 0]
                        }
                    ],
                    "lighting_scenario": "StationaryDirectionalLight",
                    "world_bounds": {
                        "min": [-10000, -10000, -1000],
                        "max": [10000, 10000, 2000]
                    },
                    "total_actors": 15,
                    "total_streaming_levels": 2,
                    "total_landscapes": 1,
                    "memory_usage": {
                        "level": "12.5 MB",
                        "streaming": "4.2 MB", 
                        "landscapes": "8.7 MB",
                        "total": "25.4 MB"
                    },
                    "performance_stats": {
                        "draw_calls": 45,
                        "triangles": 125000,
                        "frame_time": 16.7
                    },
                    "query_time": 0.05
                }
            },
            
            # UMG commands
            "create_umg_widget_blueprint": {
                "success": True,
                "result": "Widget blueprint created successfully"
            },
            "add_text_block_to_widget": {
                "success": True,
                "result": "Text block added successfully"
            },
            "add_button_to_widget": {
                "success": True,
                "result": "Button added successfully"
            },
            "bind_widget_event": {
                "success": True,
                "result": "Event bound successfully"
            }
        }
        
    def get_error_test_cases(self) -> Dict[str, Dict[str, Any]]:
        """Get test cases for error handling validation."""
        return {
            "invalid_command": {
                "command": "nonexistent_command",
                "params": {},
                "expected_response": {
                    "status": "error",
                    "error": "Unknown command"
                }
            },
            "missing_required_param": {
                "command": "spawn_actor",
                "params": {"name": "TestActor"},  # Missing type and location
                "expected_response": {
                    "status": "error", 
                    "error": "Missing required parameter"
                }
            },
            "invalid_actor_type": {
                "command": "spawn_actor",
                "params": {
                    "name": "TestActor",
                    "type": "NonexistentActorType",
                    "location": [0, 0, 0]
                },
                "expected_response": {
                    "status": "error",
                    "error": "Invalid actor type"
                }
            },
            "duplicate_actor_name": {
                "command": "spawn_actor",
                "params": {
                    "name": "ExistingActor",
                    "type": "StaticMeshActor",
                    "location": [0, 0, 0]
                },
                "expected_response": {
                    "status": "error",
                    "error": "Actor with name already exists"
                }
            },
            "invalid_blueprint_path": {
                "command": "create_blueprint",
                "params": {
                    "name": "TestBP",
                    "parent_class": "Actor",
                    "path": "/Invalid/Path"
                },
                "expected_response": {
                    "status": "error",
                    "error": "Invalid path"
                }
            },
            "connection_timeout": {
                "command": "get_actors_in_level",
                "params": {},
                "expected_response": {
                    "status": "error",
                    "error": "Connection timeout"
                },
                "simulate_timeout": True
            }
        }
        
    def get_performance_test_data(self) -> Dict[str, Any]:
        """Get test data for performance testing."""
        return {
            "large_actor_batch": {
                "actor_count": 100,
                "actor_template": self.actors["simple_cube"],
                "spawn_pattern": "grid",
                "grid_spacing": 100
            },
            "complex_blueprint": {
                "component_count": 20,
                "variable_count": 50,
                "function_count": 10
            },
            "asset_batch_operations": {
                "asset_count": 50,
                "operation_types": ["load", "save", "find", "delete"]
            }
        }
        
    def save_test_data_to_json(self, output_dir: str):
        """Save test data to JSON files for external use."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Convert dataclasses to dictionaries
        data = {
            "actors": {k: v.__dict__ for k, v in self.actors.items()},
            "blueprints": {k: v.__dict__ for k, v in self.blueprints.items()},
            "assets": {k: v.__dict__ for k, v in self.assets.items()},
            "levels": {k: v.__dict__ for k, v in self.levels.items()},
            "widgets": {k: v.__dict__ for k, v in self.widgets.items()},
            "mock_responses": self.get_mock_responses(),
            "error_cases": self.get_error_test_cases(),
            "performance_data": self.get_performance_test_data()
        }
        
        for category, category_data in data.items():
            file_path = output_path / f"{category}.json"
            with open(file_path, 'w') as f:
                json.dump(category_data, f, indent=2)
                
        print(f"Test data saved to {output_path}")

# Global instance
_test_data_manager = None

def get_test_data_manager() -> TestDataManager:
    """Get or create the global test data manager instance."""
    global _test_data_manager
    if _test_data_manager is None:
        _test_data_manager = TestDataManager()
    return _test_data_manager

# Convenience functions
def get_actor_data(key: str) -> ActorTestData:
    """Get actor test data by key."""
    return get_test_data_manager().get_actor_data(key)

def get_blueprint_data(key: str) -> BlueprintTestData:
    """Get blueprint test data by key."""
    return get_test_data_manager().get_blueprint_data(key)

def get_asset_data(key: str) -> AssetTestData:
    """Get asset test data by key."""
    return get_test_data_manager().get_asset_data(key)

def get_level_data(key: str) -> LevelTestData:
    """Get level test data by key."""
    return get_test_data_manager().get_level_data(key)

def get_widget_data(key: str) -> UMGTestData:
    """Get widget test data by key."""
    return get_test_data_manager().get_widget_data(key)

def get_landscape_data(key: str) -> Dict[str, Any]:
    """Get landscape test data by key."""
    return get_test_data_manager().get_landscape_data(key)

def get_world_operations_data() -> Dict[str, Any]:
    """Get world/level operations test data."""
    return get_test_data_manager().get_world_operations_data()

def get_level_creation_data() -> Dict[str, Any]:
    """Get level creation test data."""
    return get_test_data_manager().get_level_creation_data()

def get_streaming_levels_data() -> Dict[str, Any]:
    """Get streaming levels test data."""
    return get_test_data_manager().get_streaming_levels_data()

def get_landscape_operations_data() -> Dict[str, Any]:
    """Get landscape operations test data."""
    return get_test_data_manager().get_landscape_operations_data()

if __name__ == "__main__":
    # Generate test data files
    manager = TestDataManager()
    manager.save_test_data_to_json("test_data_output")
    print("Test data files generated successfully!")