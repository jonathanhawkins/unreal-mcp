#include "Commands/Editor/AssetTools/UnrealMCPContentBrowserCommands.h"
#include "Engine/Engine.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/AssetData.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

FString FUnrealMCPContentBrowserCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("list_assets"))
    {
        return ListAssets(Params);
    }
    else if (CommandType == TEXT("get_asset_metadata"))
    {
        return GetAssetMetadata(Params);
    }
    else if (CommandType == TEXT("search_assets"))
    {
        return SearchAssets(Params);
    }
    
    return FString::Printf(TEXT("{\"success\":false,\"error\":\"Unknown content browser command: %s\"}"), *CommandType);
}

FString FUnrealMCPContentBrowserCommands::ListAssets(const TSharedPtr<FJsonObject>& Params)
{
    FString Path = Params->GetStringField(TEXT("path"));
    FString TypeFilter = "";
    Params->TryGetStringField(TEXT("type_filter"), TypeFilter);
    bool bRecursive = false;
    Params->TryGetBoolField(TEXT("recursive"), bRecursive);
    
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
    
    TArray<FAssetData> AssetData;
    FARFilter Filter;
    
    if (!Path.IsEmpty())
    {
        Filter.PackagePaths.Add(FName(*Path));
        Filter.bRecursivePaths = bRecursive;
    }
    
    if (!TypeFilter.IsEmpty())
    {
        Filter.ClassPaths.Add(FTopLevelAssetPath(TEXT("/Script/Engine"), FName(*TypeFilter)));
    }
    
    AssetRegistry.GetAssets(Filter, AssetData);
    
    TArray<TSharedPtr<FJsonValue>> AssetArray;
    for (const FAssetData& Asset : AssetData)
    {
        AssetArray.Add(MakeShareable(new FJsonValueObject(AssetToJson(Asset))));
    }
    
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    Result->SetArrayField(TEXT("assets"), AssetArray);
    Result->SetNumberField(TEXT("count"), AssetData.Num());
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

FString FUnrealMCPContentBrowserCommands::GetAssetMetadata(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
    
    FAssetData AssetData = AssetRegistry.GetAssetByObjectPath(FSoftObjectPath(AssetPath));
    
    if (!AssetData.IsValid())
    {
        return FString::Printf(TEXT("{\"success\":false,\"error\":\"Asset not found: %s\"}"), *AssetPath);
    }
    
    TSharedPtr<FJsonObject> MetadataJson = AssetToJson(AssetData);
    
    // Add additional metadata
    MetadataJson->SetStringField(TEXT("package_name"), AssetData.PackageName.ToString());
    MetadataJson->SetStringField(TEXT("asset_name"), AssetData.AssetName.ToString());
    
    // Add tags
    TSharedPtr<FJsonObject> TagsJson = MakeShareable(new FJsonObject);
    for (const auto& Tag : AssetData.TagsAndValues)
    {
        TagsJson->SetStringField(Tag.Key.ToString(), Tag.Value.AsString());
    }
    MetadataJson->SetObjectField(TEXT("tags"), TagsJson);
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(MetadataJson.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

FString FUnrealMCPContentBrowserCommands::SearchAssets(const TSharedPtr<FJsonObject>& Params)
{
    FString SearchText = Params->GetStringField(TEXT("search_text"));
    FString TypeFilter = "";
    Params->TryGetStringField(TEXT("type_filter"), TypeFilter);
    
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
    
    TArray<FAssetData> AssetData;
    FARFilter Filter;
    
    if (!TypeFilter.IsEmpty())
    {
        Filter.ClassPaths.Add(FTopLevelAssetPath(TEXT("/Script/Engine"), FName(*TypeFilter)));
    }
    
    AssetRegistry.GetAssets(Filter, AssetData);
    
    // Filter by search text
    TArray<TSharedPtr<FJsonValue>> SearchResults;
    for (const FAssetData& Asset : AssetData)
    {
        FString AssetName = Asset.AssetName.ToString();
        FString PackagePath = Asset.PackagePath.ToString();
        
        if (AssetName.Contains(SearchText, ESearchCase::IgnoreCase) || 
            PackagePath.Contains(SearchText, ESearchCase::IgnoreCase))
        {
            SearchResults.Add(MakeShareable(new FJsonValueObject(AssetToJson(Asset))));
        }
    }
    
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    Result->SetArrayField(TEXT("assets"), SearchResults);
    Result->SetNumberField(TEXT("count"), SearchResults.Num());
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

TSharedPtr<FJsonObject> FUnrealMCPContentBrowserCommands::AssetToJson(const FAssetData& AssetData)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    
    JsonObject->SetStringField(TEXT("name"), AssetData.AssetName.ToString());
    JsonObject->SetStringField(TEXT("path"), AssetData.GetObjectPathString());
    JsonObject->SetStringField(TEXT("package_path"), AssetData.PackagePath.ToString());
    JsonObject->SetStringField(TEXT("class"), GetAssetTypeName(AssetData.GetClass()));
    
    return JsonObject;
}

FString FUnrealMCPContentBrowserCommands::GetAssetTypeName(UClass* AssetClass)
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