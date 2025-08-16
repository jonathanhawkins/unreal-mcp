#pragma once

#include "CoreMinimal.h"

class UNREALMCP_API FUnrealMCPLandscapeCommands
{
public:
    static FString HandleCommand(const FString& CommandType, const TSharedPtr<FJsonObject>& Params);

private:
    // Landscape operations
    static FString CreateLandscape(const TSharedPtr<FJsonObject>& Params);
    static FString ModifyLandscape(const TSharedPtr<FJsonObject>& Params);
    static FString PaintLandscapeLayer(const TSharedPtr<FJsonObject>& Params);
    static FString GetLandscapeInfo(const TSharedPtr<FJsonObject>& Params);
    
    // Utility functions
    static TSharedPtr<FJsonObject> LandscapeToJson(class ALandscape* Landscape);
};