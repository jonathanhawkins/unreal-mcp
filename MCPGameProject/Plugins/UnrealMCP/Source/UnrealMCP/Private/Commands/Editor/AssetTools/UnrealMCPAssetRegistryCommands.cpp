#include "Commands/Editor/AssetTools/UnrealMCPAssetRegistryCommands.h"
#include "Engine/Engine.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/AssetData.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

FString FUnrealMCPAssetRegistryCommands::HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params)
{
    if (CommandType == TEXT("get_asset_references"))
    {
        return GetAssetReferences(Params);
    }
    else if (CommandType == TEXT("get_asset_dependencies"))
    {
        return GetAssetDependencies(Params);
    }
    
    return FString::Printf(TEXT("{\"success\":false,\"error\":\"Unknown asset registry command: %s\"}"), *CommandType);
}

FString FUnrealMCPAssetRegistryCommands::GetAssetReferences(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
    
    TArray<FName> Referencers;
    AssetRegistry.GetReferencers(FName(*AssetPath), Referencers);
    
    TArray<TSharedPtr<FJsonValue>> ReferencerArray;
    for (const FName& Referencer : Referencers)
    {
        ReferencerArray.Add(MakeShareable(new FJsonValueString(Referencer.ToString())));
    }
    
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    Result->SetArrayField(TEXT("referencers"), ReferencerArray);
    Result->SetNumberField(TEXT("count"), Referencers.Num());
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

FString FUnrealMCPAssetRegistryCommands::GetAssetDependencies(const TSharedPtr<FJsonObject>& Params)
{
    FString AssetPath = Params->GetStringField(TEXT("asset_path"));
    
    FAssetRegistryModule& AssetRegistryModule = FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");
    IAssetRegistry& AssetRegistry = AssetRegistryModule.Get();
    
    TArray<FName> Dependencies;
    AssetRegistry.GetDependencies(FName(*AssetPath), Dependencies);
    
    TArray<TSharedPtr<FJsonValue>> DependencyArray;
    for (const FName& Dependency : Dependencies)
    {
        DependencyArray.Add(MakeShareable(new FJsonValueString(Dependency.ToString())));
    }
    
    TSharedPtr<FJsonObject> Result = MakeShareable(new FJsonObject);
    Result->SetArrayField(TEXT("dependencies"), DependencyArray);
    Result->SetNumberField(TEXT("count"), Dependencies.Num());
    
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);
    
    return FString::Printf(TEXT("{\"success\":true,\"result\":%s}"), *OutputString);
}

TSharedPtr<FJsonObject> FUnrealMCPAssetRegistryCommands::AssetToJson(const FAssetData& AssetData)
{
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject);
    
    JsonObject->SetStringField(TEXT("name"), AssetData.AssetName.ToString());
    JsonObject->SetStringField(TEXT("path"), AssetData.GetObjectPathString());
    JsonObject->SetStringField(TEXT("package_path"), AssetData.PackagePath.ToString());
    JsonObject->SetStringField(TEXT("class"), GetAssetTypeName(AssetData.GetClass()));
    
    return JsonObject;
}

FString FUnrealMCPAssetRegistryCommands::GetAssetTypeName(UClass* AssetClass)
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