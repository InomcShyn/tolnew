"""
Script để sao chép chính xác profile GPMLogin
"""
import json
import os
import shutil

def copy_exact_gpm_profile():
    """Sao chép chính xác profile GPMLogin"""
    
    # Đường dẫn profile GPMLogin và tool
    gpm_profile = r"c:\GPM-profile\gWabXcwoWs-01102025"
    tool_profile = r"c:\Users\admin\tolnew\chrome_profiles\gWabXcwoWs-01102025"
    
    print(f"[COPY] Sao chep tu: {gpm_profile}")
    print(f"[COPY] Den: {tool_profile}")
    
    # 1. Sao chép Local State
    gpm_local_state = os.path.join(gpm_profile, "Local State")
    tool_local_state = os.path.join(tool_profile, "Local State")
    
    if os.path.exists(gpm_local_state):
        shutil.copy2(gpm_local_state, tool_local_state)
        print(f"  [OK] Da sao chep Local State")
    
    # 2. Sao chép Preferences
    gpm_preferences = os.path.join(gpm_profile, "Default", "Preferences")
    tool_preferences = os.path.join(tool_profile, "Default", "Preferences")
    
    if os.path.exists(gpm_preferences):
        shutil.copy2(gpm_preferences, tool_preferences)
        print(f"  [OK] Da sao chep Preferences")
    
    # 3. Sao chép toàn bộ thư mục Default
    gpm_default = os.path.join(gpm_profile, "Default")
    tool_default = os.path.join(tool_profile, "Default")
    
    if os.path.exists(gpm_default):
        if os.path.exists(tool_default):
            shutil.rmtree(tool_default)
        shutil.copytree(gpm_default, tool_default)
        print(f"  [OK] Da sao chep thu muc Default")
    
    # 4. Sao chép các file khác
    files_to_copy = [
        "Variations",
        "chrome_debug.log", 
        "BrowserMetrics-spare.pma",
        "first_party_sets.db",
        "first_party_sets.db-journal",
        "Last Browser",
        "CrashpadMetrics-active.pma",
        "DevToolsActivePort",
        "Last Version",
        "First Run"
    ]
    
    for file_name in files_to_copy:
        gpm_file = os.path.join(gpm_profile, file_name)
        tool_file = os.path.join(tool_profile, file_name)
        
        if os.path.exists(gpm_file):
            if os.path.isdir(gpm_file):
                if os.path.exists(tool_file):
                    shutil.rmtree(tool_file)
                shutil.copytree(gpm_file, tool_file)
            else:
                shutil.copy2(gpm_file, tool_file)
            print(f"  [OK] Da sao chep {file_name}")
    
    # 5. Sao chép các thư mục quan trọng
    dirs_to_copy = [
        "component_crx_cache",
        "OriginTrials", 
        "extensions_crx_cache",
        "FirstPartySetsPreloaded",
        "GraphiteDawnCache",
        "GrShaderCache",
        "ShaderCache",
        "OpenCookieDatabase",
        "ProbabilisticRevealTokenRegistry",
        "WasmTtsEngine",
        "hyphen-data",
        "TpcdMetadata",
        "ZxcvbnData",
        "MEIPreload",
        "SafetyTips",
        "PKIMetadata",
        "TrustTokenKeyCommitments",
        "FileTypePolicies",
        "SSLErrorAssistant",
        "Subresource Filter",
        "WidevineCdm",
        "MediaFoundationWidevineCdm",
        "OnDeviceHeadSuggestModel",
        "RecoveryImproved",
        "PrivacySandboxAttestationsPreloaded",
        "Safe Browsing",
        "segmentation_platform",
        "BrowserMetrics",
        "Crashpad",
        "Crowd Deny",
        "CookieReadinessList",
        "CertificateRevocation",
        "AutofillStates",
        "AmountExtractionHeuristicRegexes"
    ]
    
    for dir_name in dirs_to_copy:
        gpm_dir = os.path.join(gpm_profile, dir_name)
        tool_dir = os.path.join(tool_profile, dir_name)
        
        if os.path.exists(gpm_dir):
            if os.path.exists(tool_dir):
                shutil.rmtree(tool_dir)
            shutil.copytree(gpm_dir, tool_dir)
            print(f"  [OK] Da sao chep thu muc {dir_name}")

if __name__ == "__main__":
    copy_exact_gpm_profile()
    print("\n[DONE] Hoan tat sao chep profile GPMLogin!")
