#include "Commands/Engine/World/UnrealMCPWorldCommands.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/Level.h"
#include "Engine/LevelStreaming.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

// Forward declaration for LevelToJson from LevelCommands
extern TSharedPtr<FJsonObject> LevelToJson(ULevel* Level);

FString FUnrealMCPWorldCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("get_current_level_info"))
    {
        return GetCurrentLevelInfo(Params);
    }
    
    return TEXT("{\"success\":false,\"error\":\"Unknown world command\"}");
}

FString FUnrealMCPWorldCommands::GetCurrentLevelInfo(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        TSharedPtr<FJsonObject> WorldInfo = MakeShareable(new FJsonObject);
        WorldInfo->SetStringField(TEXT("world_name"), World->GetMapName());
        WorldInfo->SetStringField(TEXT("world_type"), GetWorldTypeName(World->WorldType));
        WorldInfo->SetNumberField(TEXT("num_levels"), World->GetNumLevels());
        
        // Get persistent level info
        if (World->PersistentLevel)
        {
            // Create basic level info inline to avoid external dependency
            TSharedPtr<FJsonObject> PersistentLevelInfo = MakeShareable(new FJsonObject);
            PersistentLevelInfo->SetStringField(TEXT("name"), World->PersistentLevel->GetName());
            PersistentLevelInfo->SetNumberField(TEXT("num_actors"), World->PersistentLevel->Actors.Num());
            PersistentLevelInfo->SetBoolField(TEXT("is_visible"), World->PersistentLevel->bIsVisible);
            
            WorldInfo->SetObjectField(TEXT("persistent_level"), PersistentLevelInfo);
        }

        // Get streaming levels
        TArray<TSharedPtr<FJsonValue>> StreamingLevels;
        for (ULevelStreaming* StreamingLevel : World->GetStreamingLevels())
        {
            if (StreamingLevel)
            {
                TSharedPtr<FJsonObject> StreamingLevelInfo = MakeShareable(new FJsonObject);
                StreamingLevelInfo->SetStringField(TEXT("package_name"), StreamingLevel->GetWorldAssetPackageName());
                StreamingLevelInfo->SetBoolField(TEXT("is_loaded"), StreamingLevel->IsLevelLoaded());
                StreamingLevelInfo->SetBoolField(TEXT("is_visible"), StreamingLevel->IsLevelVisible());
                StreamingLevels.Add(MakeShareable(new FJsonValueObject(StreamingLevelInfo)));
            }
        }
        WorldInfo->SetArrayField(TEXT("streaming_levels"), StreamingLevels);

        FString OutputString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
        FJsonSerializer::Serialize(WorldInfo.ToSharedRef(), Writer);
        
        return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in GetCurrentLevelInfo: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPWorldCommands::GetWorldTypeName(EWorldType::Type WorldType)
{
    switch (WorldType)
    {
        case EWorldType::None: return TEXT("None");
        case EWorldType::Game: return TEXT("Game");
        case EWorldType::Editor: return TEXT("Editor");
        case EWorldType::PIE: return TEXT("PIE");
        case EWorldType::EditorPreview: return TEXT("EditorPreview");
        case EWorldType::GamePreview: return TEXT("GamePreview");
        case EWorldType::Inactive: return TEXT("Inactive");
        default: return TEXT("Unknown");
    }
}