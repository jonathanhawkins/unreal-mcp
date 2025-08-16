#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPAssetCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Core asset operations
    static FString LoadAsset(const TSharedPtr<FJsonObject>& Params);
    static FString SaveAsset(const TSharedPtr<FJsonObject>& Params);
    static FString DuplicateAsset(const TSharedPtr<FJsonObject>& Params);
    static FString DeleteAsset(const TSharedPtr<FJsonObject>& Params);
    static FString RenameAsset(const TSharedPtr<FJsonObject>& Params);
    static FString MoveAsset(const TSharedPtr<FJsonObject>& Params);
    
    // Import/Export
    static FString ImportAsset(const TSharedPtr<FJsonObject>& Params);
    static FString ExportAsset(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static TSharedPtr<FJsonObject> AssetToJson(const FAssetData& AssetData);
    static FString GetAssetTypeName(UClass* AssetClass);
};