#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPLevelCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Level management
    static FString CreateLevel(const TSharedPtr<FJsonObject>& Params);
    static FString SaveLevel(const TSharedPtr<FJsonObject>& Params);
    static FString LoadLevel(const TSharedPtr<FJsonObject>& Params);
    static FString SetLevelVisibility(const TSharedPtr<FJsonObject>& Params);
    
    // Streaming levels
    static FString CreateStreamingLevel(const TSharedPtr<FJsonObject>& Params);
    static FString LoadStreamingLevel(const TSharedPtr<FJsonObject>& Params);
    static FString UnloadStreamingLevel(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static TSharedPtr<FJsonObject> LevelToJson(ULevel* Level);
};