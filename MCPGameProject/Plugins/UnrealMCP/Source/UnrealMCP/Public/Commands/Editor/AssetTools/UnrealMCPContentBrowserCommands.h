#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPContentBrowserCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Asset listing and browsing
    static FString ListAssets(const TSharedPtr<FJsonObject>& Params);
    static FString GetAssetMetadata(const TSharedPtr<FJsonObject>& Params);
    static FString SearchAssets(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static TSharedPtr<FJsonObject> AssetToJson(const FAssetData& AssetData);
    static FString GetAssetTypeName(UClass* AssetClass);
};