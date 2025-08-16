#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPWorldCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Runtime world operations
    static FString GetCurrentLevelInfo(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static FString GetWorldTypeName(EWorldType::Type WorldType);
};