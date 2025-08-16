#include "Commands/Editor/LevelEditor/UnrealMCPLevelCommands.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/Level.h"
#include "Engine/LevelStreaming.h"
#include "LevelUtils.h"
#include "EditorLevelLibrary.h"
#include "EditorAssetLibrary.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "HAL/FileManager.h"
#include "Misc/PackageName.h"
#include "UObject/SavePackage.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "FileHelpers.h"
#include "Subsystems/EditorActorSubsystem.h"
#include "Subsystems/UnrealEditorSubsystem.h"
#include "LevelEditorSubsystem.h"
#include "Engine/LevelStreaming.h"
#include "Engine/LevelStreamingDynamic.h"

FString FUnrealMCPLevelCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("create_level"))
    {
        return CreateLevel(Params);
    }
    else if (CommandType == TEXT("save_level"))
    {
        return SaveLevel(Params);
    }
    else if (CommandType == TEXT("load_level"))
    {
        return LoadLevel(Params);
    }
    else if (CommandType == TEXT("set_level_visibility"))
    {
        return SetLevelVisibility(Params);
    }
    else if (CommandType == TEXT("create_streaming_level"))
    {
        return CreateStreamingLevel(Params);
    }
    else if (CommandType == TEXT("load_streaming_level"))
    {
        return LoadStreamingLevel(Params);
    }
    else if (CommandType == TEXT("unload_streaming_level"))
    {
        return UnloadStreamingLevel(Params);
    }
    
    return TEXT("{\"success\":false,\"error\":\"Unknown level command\"}");
}

FString FUnrealMCPLevelCommands::CreateLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelName;
        if (!Params->TryGetStringField(TEXT("level_name"), LevelName) || LevelName.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_name parameter is required\"}");
        }

        FString LevelPath = TEXT("/Game/") + LevelName;
        
        // Create new level using the modern API
        ULevelEditorSubsystem* LevelEditorSubsystem = GEditor->GetEditorSubsystem<ULevelEditorSubsystem>();
        if (!LevelEditorSubsystem)
        {
            return TEXT("{\"success\":false,\"error\":\"Failed to get LevelEditorSubsystem\"}");
        }
        
        bool bSuccess = LevelEditorSubsystem->NewLevel(LevelPath);
        if (!bSuccess)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to create level: %s\"}"), *LevelName);
        }
        
        UWorld* NewWorld = GEditor->GetEditorWorldContext().World();
        if (!NewWorld)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to create level: %s\"}"), *LevelName);
        }

        // Get level info
        TSharedPtr<FJsonObject> LevelInfo = LevelToJson(NewWorld->PersistentLevel);
        
        FString OutputString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
        FJsonSerializer::Serialize(LevelInfo.ToSharedRef(), Writer);
        
        return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in CreateLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::SaveLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        // Save current level using the modern API
        ULevelEditorSubsystem* LevelEditorSubsystem = GEditor->GetEditorSubsystem<ULevelEditorSubsystem>();
        if (!LevelEditorSubsystem)
        {
            return TEXT("{\"success\":false,\"error\":\"Failed to get LevelEditorSubsystem\"}");
        }
        
        bool bSaved = LevelEditorSubsystem->SaveCurrentLevel();
        if (!bSaved)
        {
            return TEXT("{\"success\":false,\"error\":\"Failed to save level\"}");
        }

        FString LevelName = World->GetMapName();
        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Level saved: %s\"}"), *LevelName);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in SaveLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::LoadLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelPath;
        if (!Params->TryGetStringField(TEXT("level_path"), LevelPath) || LevelPath.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_path parameter is required\"}");
        }

        // Load level
        ULevelEditorSubsystem* LevelEditorSubsystem = GEditor->GetEditorSubsystem<ULevelEditorSubsystem>();
        if (!LevelEditorSubsystem)
        {
            return TEXT("{\"success\":false,\"error\":\"Failed to get LevelEditorSubsystem\"}");
        }
        
        bool bLoaded = LevelEditorSubsystem->LoadLevel(LevelPath);
        if (!bLoaded)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to load level: %s\"}"), *LevelPath);
        }

        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Level loaded: %s\"}"), *LevelPath);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in LoadLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::SetLevelVisibility(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelName;
        bool bVisible = true;
        
        if (!Params->TryGetStringField(TEXT("level_name"), LevelName) || LevelName.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_name parameter is required\"}");
        }
        
        Params->TryGetBoolField(TEXT("visible"), bVisible);

        // For UE 5.6, SetLevelVisibility is not available in LevelEditorSubsystem
        // We'll implement a basic version using level streaming
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }
        
        bool bSuccess = false;
        // Find the streaming level and set its visibility
        for (ULevelStreaming* StreamingLevel : World->GetStreamingLevels())
        {
            if (StreamingLevel && StreamingLevel->GetWorldAssetPackageName() == LevelName)
            {
                StreamingLevel->SetShouldBeVisible(bVisible);
                bSuccess = true;
                break;
            }
        }
        if (!bSuccess)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to set visibility for level: %s\"}"), *LevelName);
        }

        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Set level %s visibility to %s\"}"), 
                              *LevelName, bVisible ? TEXT("visible") : TEXT("hidden"));
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in SetLevelVisibility: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::CreateStreamingLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelPath;
        if (!Params->TryGetStringField(TEXT("level_path"), LevelPath) || LevelPath.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_path parameter is required\"}");
        }

        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        // Create streaming level manually since AddLevelToWorld is not available
        UClass* StreamingClass = ULevelStreamingDynamic::StaticClass();
        ULevelStreaming* StreamingLevel = NewObject<ULevelStreaming>(World, StreamingClass);
        if (StreamingLevel)
        {
            StreamingLevel->SetWorldAssetByPackageName(FName(*LevelPath));
            World->AddStreamingLevel(StreamingLevel);
        }
        if (!StreamingLevel)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to create streaming level: %s\"}"), *LevelPath);
        }

        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Created streaming level: %s\"}"), *LevelPath);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in CreateStreamingLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::LoadStreamingLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelName;
        if (!Params->TryGetStringField(TEXT("level_name"), LevelName) || LevelName.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_name parameter is required\"}");
        }

        ULevelEditorSubsystem* LevelEditorSubsystem = GEditor->GetEditorSubsystem<ULevelEditorSubsystem>();
        if (!LevelEditorSubsystem)
        {
            return TEXT("{\"success\":false,\"error\":\"Failed to get LevelEditorSubsystem\"}");
        }
        
        bool bLoaded = LevelEditorSubsystem->LoadLevel(LevelName);
        if (!bLoaded)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to load streaming level: %s\"}"), *LevelName);
        }

        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Loaded streaming level: %s\"}"), *LevelName);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in LoadStreamingLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLevelCommands::UnloadStreamingLevel(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LevelName;
        if (!Params->TryGetStringField(TEXT("level_name"), LevelName) || LevelName.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"level_name parameter is required\"}");
        }

        // Implement UnloadLevel manually since it's not available in LevelEditorSubsystem
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }
        
        bool bUnloaded = false;
        // Find and remove the streaming level
        for (int32 i = World->GetStreamingLevels().Num() - 1; i >= 0; i--)
        {
            ULevelStreaming* StreamingLevel = World->GetStreamingLevels()[i];
            if (StreamingLevel && StreamingLevel->GetWorldAssetPackageName() == LevelName)
            {
                World->RemoveStreamingLevel(StreamingLevel);
                bUnloaded = true;
                break;
            }
        }
        if (!bUnloaded)
        {
            return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to unload streaming level: %s\"}"), *LevelName);
        }

        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Unloaded streaming level: %s\"}"), *LevelName);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in UnloadStreamingLevel: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

TSharedPtr<FJsonObject> FUnrealMCPLevelCommands::LevelToJson(ULevel* Level)
{
    TSharedPtr<FJsonObject> LevelObj = MakeShareable(new FJsonObject);
    
    if (!Level)
    {
        return LevelObj;
    }

    LevelObj->SetStringField(TEXT("name"), Level->GetName());
    LevelObj->SetNumberField(TEXT("num_actors"), Level->Actors.Num());
    LevelObj->SetBoolField(TEXT("is_visible"), Level->bIsVisible);
    
    if (Level->GetOuter())
    {
        LevelObj->SetStringField(TEXT("package_name"), Level->GetOuter()->GetName());
    }

    // Add basic bounds info by calculating from actors
    if (Level->Actors.Num() > 0)
    {
        FBox LevelBounds(ForceInit);
        bool bHasValidBounds = false;
        
        for (AActor* Actor : Level->Actors)
        {
            if (Actor && Actor->GetRootComponent())
            {
                FBox ActorBounds = Actor->GetRootComponent()->Bounds.GetBox();
                if (ActorBounds.IsValid)
                {
                    if (!bHasValidBounds)
                    {
                        LevelBounds = ActorBounds;
                        bHasValidBounds = true;
                    }
                    else
                    {
                        LevelBounds += ActorBounds;
                    }
                }
            }
        }
        
        if (bHasValidBounds)
        {
            TSharedPtr<FJsonObject> BoundsObj = MakeShareable(new FJsonObject);
            FVector Origin = LevelBounds.GetCenter();
            FVector Extent = LevelBounds.GetExtent();
            
            BoundsObj->SetNumberField(TEXT("origin_x"), Origin.X);
            BoundsObj->SetNumberField(TEXT("origin_y"), Origin.Y);
            BoundsObj->SetNumberField(TEXT("origin_z"), Origin.Z);
            BoundsObj->SetNumberField(TEXT("extent_x"), Extent.X);
            BoundsObj->SetNumberField(TEXT("extent_y"), Extent.Y);
            BoundsObj->SetNumberField(TEXT("extent_z"), Extent.Z);
            
            LevelObj->SetObjectField(TEXT("bounds"), BoundsObj);
        }
    }

    return LevelObj;
}