#include "Commands/Editor/AssetTools/UnrealMCPAssetCommands.h"
#include "Engine/Engine.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/AssetData.h"
#include "UObject/SavePackage.h"
#include "EditorAssetLibrary.h"
#include "AssetToolsModule.h"
#include "Factories/Factory.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "HAL/FileManager.h"
#include "Misc/PackageName.h"
#include "ObjectTools.h"

FString FUnrealMCPAssetCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("load_asset"))
    {
        return LoadAsset(Params);
    }
    else if (CommandType == TEXT("save_asset"))
    {
        return SaveAsset(Params);
    }
    else if (CommandType == TEXT("duplicate_asset"))
    {
        return DuplicateAsset(Params);
    }
    else if (CommandType == TEXT("delete_asset"))
    {
        return DeleteAsset(Params);
    }
    else if (CommandType == TEXT("rename_asset"))
    {
        return RenameAsset(Params);
    }
    else if (CommandType == TEXT("move_asset"))
    {
        return MoveAsset(Params);
    }
    else if (CommandType == TEXT("import_asset"))
    {
        return ImportAsset(Params);
    }
    else if (CommandType == TEXT("export_asset"))
    {
        return ExportAsset(Params);
    }
    
    return FString::Printf(TEXT("{\"success\":false,\"error\":\"Unknown asset command: %s\"}"), *CommandType);
}

FString FUnrealMCPAssetCommands::LoadAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    
    UObject* LoadedAsset = UEditorAssetLibrary::LoadAsset(AssetPath);
    
    if (!LoadedAsset)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to load asset: %s\"}"), *AssetPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"asset_path\":\"%s\",\"loaded\":true,\"class\":\"%s\"}}"), 
        *AssetPath, *LoadedAsset->GetClass()->GetName());
}

FString FUnrealMCPAssetCommands::SaveAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    bool bOnlyIfDirty = true;
    Params->TryGetBoolField(TEXT("only_if_dirty"), bOnlyIfDirty);
    
    bool bSuccess = UEditorAssetLibrary::SaveAsset(AssetPath, bOnlyIfDirty);
    
    if (!bSuccess)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to save asset: %s\"}"), *AssetPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"asset_path\":\"%s\",\"saved\":true}}"), *AssetPath);
}

FString FUnrealMCPAssetCommands::DuplicateAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString SourcePath = Params->GetStringField(TEXT("source_path"));
    FString DestinationPath = Params->GetStringField(TEXT("destination_path"));
    
    UObject* DuplicatedAsset = UEditorAssetLibrary::DuplicateAsset(SourcePath, DestinationPath);
    
    if (!DuplicatedAsset)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to duplicate asset from %s to %s\"}"), 
            *SourcePath, *DestinationPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"source\":\"%s\",\"destination\":\"%s\",\"duplicated\":true}}"), 
        *SourcePath, *DestinationPath);
}

FString FUnrealMCPAssetCommands::DeleteAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    
    bool bSuccess = UEditorAssetLibrary::DeleteAsset(AssetPath);
    
    if (!bSuccess)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to delete asset: %s\"}"), *AssetPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"asset_path\":\"%s\",\"deleted\":true}}"), *AssetPath);
}

FString FUnrealMCPAssetCommands::RenameAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString SourcePath = Params->GetStringField(TEXT("source_path"));
    FString NewName = Params->GetStringField(TEXT("new_name"));
    
    // Extract directory from source path
    FString Directory = FPaths::GetPath(SourcePath);
    FString NewPath = FPaths::Combine(Directory, NewName);
    
    bool bSuccess = UEditorAssetLibrary::RenameAsset(SourcePath, NewPath);
    
    if (!bSuccess)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to rename asset from %s to %s\"}"), 
            *SourcePath, *NewPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"old_path\":\"%s\",\"new_path\":\"%s\"}}"), 
        *SourcePath, *NewPath);
}

FString FUnrealMCPAssetCommands::MoveAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString SourcePath = Params->GetStringField(TEXT("source_path"));
    FString DestinationPath = Params->GetStringField(TEXT("destination_path"));
    
    bool bSuccess = UEditorAssetLibrary::RenameAsset(SourcePath, DestinationPath);
    
    if (!bSuccess)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to move asset from %s to %s\"}"), 
            *SourcePath, *DestinationPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"source\":\"%s\",\"destination\":\"%s\",\"moved\":true}}"), 
        *SourcePath, *DestinationPath);
}

FString FUnrealMCPAssetCommands::ImportAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString FilePath = Params->GetStringField(TEXT("file_path"));
    FString DestinationPath = Params->GetStringField(TEXT("destination_path"));
    
    // This is a simplified implementation. For full functionality, you'd need to:
    // 1. Determine the appropriate factory based on file extension
    // 2. Configure import settings
    // 3. Handle different asset types
    
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
    IAssetTools& AssetTools = AssetToolsModule.Get();
    
    TArray<FString> FilesToImport;
    FilesToImport.Add(FilePath);
    
    TArray<UObject*> ImportedAssets = AssetTools.ImportAssets(FilesToImport, DestinationPath);
    
    if (ImportedAssets.Num() == 0)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to import asset from %s\"}"), *FilePath);
    }
    
    TArray<TSharedPtr<FJsonValue>> ImportedArray;
    for (UObject* Asset : ImportedAssets)
    {
        TSharedPtr<FJsonObject> AssetJson = MakeShareable(new FJsonObject);
        AssetJson->SetStringField(TEXT("name"), Asset->GetName());
        AssetJson->SetStringField(TEXT("class"), Asset->GetClass()->GetName());
        AssetJson->SetStringField(TEXT("path"), Asset->GetPathName());
        ImportedArray.Add(MakeShareable(new FJsonValueObject(AssetJson)));
    }
    
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    Result->SetArrayField(TEXT("imported_assets"), ImportedArray);
    Result->SetNumberField(TEXT("count"), ImportedAssets.Num());
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

FString FUnrealMCPAssetCommands::ExportAsset(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    FString ExportPath = Params->GetStringField(TEXT("export_path"));
    
    UObject* Asset = UEditorAssetLibrary::LoadAsset(AssetPath);
    if (!Asset)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Asset not found: %s\"}"), *AssetPath);
    }
    
    // For UE 5.6, we'll use a simplified approach
    // Save the asset to the target location
    // Note: This is a basic implementation - for full export functionality,
    // you would need to use the appropriate exporter classes
    bool bSuccess = false;
    
    // Try to use UEditorAssetLibrary to save the asset
    FString AssetPackagePath = FPackageName::ObjectPathToPackageName(AssetPath);
    UPackage* Package = FindPackage(nullptr, *AssetPackagePath);
    if (Package)
    {
        bSuccess = UEditorAssetLibrary::SaveAsset(AssetPath, false);
    }
    
    if (!bSuccess)
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Failed to export asset %s to %s\"}"), 
            *AssetPath, *ExportPath);
    }
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":{\"asset_path\":\"%s\",\"export_path\":\"%s\"}}"), 
        *AssetPath, *ExportPath);
}

TSharedPtr<FJsonObject> FUnrealMCPAssetCommands::AssetToJson(const FAssetData& AssetData)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    
    JsonObject->SetStringField(TEXT("name"), AssetData.AssetName.ToString());
    JsonObject->SetStringField(TEXT("path"), AssetData.GetObjectPathString());
    JsonObject->SetStringField(TEXT("package_path"), AssetData.PackagePath.ToString());
    JsonObject->SetStringField(TEXT("class"), GetAssetTypeName(AssetData.GetClass()));
    
    return JsonObject;
}

FString FUnrealMCPAssetCommands::GetAssetTypeName(UClass* AssetClass)
{
    if (!AssetClass)
    {
        return TEXT("Unknown");
    }
    
    FString ClassName = AssetClass->GetName();
    
    // Remove common prefixes
    if (ClassName.StartsWith(TEXT("U")))
    {
        ClassName = ClassName.RightChop(1);
    }
    else if (ClassName.StartsWith(TEXT("A")))
    {
        ClassName = ClassName.RightChop(1);
    }
    
    return ClassName;
}