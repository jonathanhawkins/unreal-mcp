#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPAssetRegistryCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Asset references and dependencies
    static FString GetAssetReferences(const TSharedPtr<FJsonObject>& Params);
    static FString GetAssetDependencies(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static TSharedPtr<FJsonObject> AssetToJson(const FAssetData& AssetData);
    static FString GetAssetTypeName(UClass* AssetClass);
};