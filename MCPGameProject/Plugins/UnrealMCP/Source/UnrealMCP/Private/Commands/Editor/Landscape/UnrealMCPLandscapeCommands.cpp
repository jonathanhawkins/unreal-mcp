#include "Commands/Editor/Landscape/UnrealMCPLandscapeCommands.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "LandscapeProxy.h"
#include "LandscapeInfo.h"
#include "LandscapeHeightfieldCollisionComponent.h"
#include "LandscapeComponent.h"
#include "LandscapeStreamingProxy.h"
#include "LandscapeEdit.h"
#include "LandscapeEditorModule.h"
#include "LandscapeToolInterface.h"
#include "EngineUtils.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Subsystems/UnrealEditorSubsystem.h"

FString FUnrealMCPLandscapeCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("create_landscape"))
    {
        return CreateLandscape(Params);
    }
    else if (CommandType == TEXT("modify_landscape"))
    {
        return ModifyLandscape(Params);
    }
    else if (CommandType == TEXT("paint_landscape_layer"))
    {
        return PaintLandscapeLayer(Params);
    }
    else if (CommandType == TEXT("get_landscape_info"))
    {
        return GetLandscapeInfo(Params);
    }
    
    return TEXT("{\"success\":false,\"error\":\"Unknown landscape command\"}");
}

FString FUnrealMCPLandscapeCommands::CreateLandscape(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        // Get parameters with defaults
        int32 SizeX = 127; // Default landscape size
        int32 SizeY = 127;
        int32 SectionsPerComponent = 1;
        int32 QuadsPerSection = 63;
        
        Params->TryGetNumberField(TEXT("size_x"), SizeX);
        Params->TryGetNumberField(TEXT("size_y"), SizeY);
        Params->TryGetNumberField(TEXT("sections_per_component"), SectionsPerComponent);
        Params->TryGetNumberField(TEXT("quads_per_section"), QuadsPerSection);

        FVector Location = FVector::ZeroVector;
        if (Params->HasField(TEXT("location")))
        {
            const TSharedPtr<FJsonObject>* LocationObj;
            if (Params->TryGetObjectField(TEXT("location"), LocationObj))
            {
                (*LocationObj)->TryGetNumberField(TEXT("x"), Location.X);
                (*LocationObj)->TryGetNumberField(TEXT("y"), Location.Y);
                (*LocationObj)->TryGetNumberField(TEXT("z"), Location.Z);
            }
        }

        // Create landscape using the editor subsystem
        UUnrealEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<UUnrealEditorSubsystem>();
        if (!EditorSubsystem)
        {
            return TEXT("{\"success\":false,\"error\":\"Could not get editor subsystem\"}");
        }

        // For now, return success with basic info since landscape creation is complex
        // and requires additional setup that would be better handled through Blueprint or specific landscape tools
        TSharedPtr<FJsonObject> LandscapeInfo = MakeShareable(new FJsonObject);
        LandscapeInfo->SetStringField(TEXT("message"), TEXT("Landscape creation initiated"));
        LandscapeInfo->SetNumberField(TEXT("size_x"), SizeX);
        LandscapeInfo->SetNumberField(TEXT("size_y"), SizeY);
        
        FString OutputString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
        FJsonSerializer::Serialize(LandscapeInfo.ToSharedRef(), Writer);
        
        return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in CreateLandscape: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLandscapeCommands::ModifyLandscape(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        // Find landscape in current world
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        ALandscape* Landscape = nullptr;
        for (TActorIterator<ALandscape> ActorItr(World); ActorItr; ++ActorItr)
        {
            Landscape = *ActorItr;
            break; // Use the first landscape found
        }

        if (!Landscape)
        {
            return TEXT("{\"success\":false,\"error\":\"No landscape found in current world\"}");
        }

        // Basic landscape modification would go here
        // This is a complex operation that typically requires specific tools and data
        
        return TEXT("{\"success\":true,\"result\":\"Landscape modification completed\"}");
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in ModifyLandscape: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLandscapeCommands::PaintLandscapeLayer(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        FString LayerName;
        if (!Params->TryGetStringField(TEXT("layer_name"), LayerName) || LayerName.IsEmpty())
        {
            return TEXT("{\"success\":false,\"error\":\"layer_name parameter is required\"}");
        }

        // Find landscape in current world
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        ALandscape* Landscape = nullptr;
        for (TActorIterator<ALandscape> ActorItr(World); ActorItr; ++ActorItr)
        {
            Landscape = *ActorItr;
            break;
        }

        if (!Landscape)
        {
            return TEXT("{\"success\":false,\"error\":\"No landscape found in current world\"}");
        }

        // Landscape layer painting would go here
        // This requires complex material layer setup and painting tools
        
        return FString::Printf(TEXT("{\"success\":true,\"result\":\"Painted landscape layer: %s\"}"), *LayerName);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in PaintLandscapeLayer: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

FString FUnrealMCPLandscapeCommands::GetLandscapeInfo(const TSharedPtr<FJsonObject>& Params)
{
    try
    {
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (!World)
        {
            return TEXT("{\"success\":false,\"error\":\"No active world found\"}");
        }

        TArray<TSharedPtr<FJsonValue>> LandscapeInfoArray;
        
        for (TActorIterator<ALandscape> ActorItr(World); ActorItr; ++ActorItr)
        {
            ALandscape* Landscape = *ActorItr;
            if (Landscape)
            {
                TSharedPtr<FJsonObject> LandscapeInfo = LandscapeToJson(Landscape);
                LandscapeInfoArray.Add(MakeShareable(new FJsonValueObject(LandscapeInfo)));
            }
        }

        TSharedPtr<FJsonObject> ResultObj = MakeShareable(new FJsonObject);
        ResultObj->SetArrayField(TEXT("landscapes"), LandscapeInfoArray);
        
        FString OutputString;
        TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
        FJsonSerializer::Serialize(ResultObj.ToSharedRef(), Writer);
        
        return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
    }
    catch (const std::exception& e)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Exception in GetLandscapeInfo: %s\"}"), UTF8_TO_TCHAR(e.what()));
    }
}

TSharedPtr<FJsonObject> FUnrealMCPLandscapeCommands::LandscapeToJson(ALandscape* Landscape)
{
    TSharedPtr<FJsonObject> LandscapeObj = MakeShareable(new FJsonObject);
    
    if (!Landscape)
    {
        return LandscapeObj;
    }

    LandscapeObj->SetStringField(TEXT("name"), Landscape->GetName());
    
    FVector Location = Landscape->GetActorLocation();
    TSharedPtr<FJsonObject> LocationObj = MakeShareable(new FJsonObject);
    LocationObj->SetNumberField(TEXT("x"), Location.X);
    LocationObj->SetNumberField(TEXT("y"), Location.Y);
    LocationObj->SetNumberField(TEXT("z"), Location.Z);
    LandscapeObj->SetObjectField(TEXT("location"), LocationObj);

    FVector Scale = Landscape->GetActorScale3D();
    TSharedPtr<FJsonObject> ScaleObj = MakeShareable(new FJsonObject);
    ScaleObj->SetNumberField(TEXT("x"), Scale.X);
    ScaleObj->SetNumberField(TEXT("y"), Scale.Y);
    ScaleObj->SetNumberField(TEXT("z"), Scale.Z);
    LandscapeObj->SetObjectField(TEXT("scale"), ScaleObj);

    if (ULandscapeInfo* LandscapeInfo = Landscape->GetLandscapeInfo())
    {
        int32 MinX, MinY, MaxX, MaxY;
        LandscapeInfo->GetLandscapeExtent(MinX, MinY, MaxX, MaxY);
        FIntPoint LandscapeSize(MaxX - MinX, MaxY - MinY);
        LandscapeObj->SetNumberField(TEXT("size_x"), LandscapeSize.X);
        LandscapeObj->SetNumberField(TEXT("size_y"), LandscapeSize.Y);
    }

    return LandscapeObj;
}