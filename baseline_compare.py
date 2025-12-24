#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 BASELINE COMPARISON TOOL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

So sánh các session baseline để xác định:
- Điểm khác biệt giữa view được tính vs không được tính
- Mốc đầu tiên bị sai lệch
- Điều kiện BẮT BUỘC để view được tính
- Tối ưu RAM an toàn vs nguy hiểm

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class BaselineComparator:
    """Compare baseline sessions"""
    
    def __init__(self, session1_dir: Path, session2_dir: Path):
        """
        Initialize comparator
        
        Args:
            session1_dir: First session directory
            session2_dir: Second session directory
        """
        self.session1_dir = Path(session1_dir)
        self.session2_dir = Path(session2_dir)
        
        # Load sessions
        self.session1 = self._load_session(self.session1_dir)
        self.session2 = self._load_session(self.session2_dir)
        
        print(f"[COMPARE] 📊 Loaded session 1: {self.session1_dir.name}")
        print(f"[COMPARE] 📊 Loaded session 2: {self.session2_dir.name}")
    
    def _load_session(self, session_dir: Path) -> Dict[str, Any]:
        """Load all stage files from session"""
        stages = []
        
        for file in sorted(session_dir.glob("*.json")):
            if file.name == "00_summary.json":
                continue
            
            with open(file, 'r', encoding='utf-8') as f:
                stages.append(json.load(f))
        
        # Load summary if exists
        summary_file = session_dir / "00_summary.json"
        summary = None
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
        
        return {
            "dir": session_dir,
            "stages": stages,
            "summary": summary
        }
    
    def compare_chrome_flags(self) -> Dict[str, Any]:
        """Compare Chrome flags between sessions"""
        # Get flags from profile_started stage
        flags1 = None
        flags2 = None
        
        for stage in self.session1["stages"]:
            if stage["stage"] == "profile_started":
                flags1 = stage.get("chrome", {}).get("flags", [])
                break
        
        for stage in self.session2["stages"]:
            if stage["stage"] == "profile_started":
                flags2 = stage.get("chrome", {}).get("flags", [])
                break
        
        if not flags1 or not flags2:
            return {"error": "Chrome flags not found in one or both sessions"}
        
        # Compare
        flags1_set = set(flags1)
        flags2_set = set(flags2)
        
        only_in_1 = flags1_set - flags2_set
        only_in_2 = flags2_set - flags1_set
        common = flags1_set & flags2_set
        
        return {
            "session1_count": len(flags1),
            "session2_count": len(flags2),
            "common_count": len(common),
            "only_in_session1": sorted(only_in_1),
            "only_in_session2": sorted(only_in_2),
            "common": sorted(common)
        }
    
    def compare_memory(self) -> Dict[str, Any]:
        """Compare memory usage across stages"""
        memory1 = []
        memory2 = []
        
        for stage in self.session1["stages"]:
            mem = stage.get("memory_total_mb") or stage.get("process", {}).get("memory_rss_mb", 0)
            memory1.append({
                "stage": stage["stage"],
                "memory_mb": mem
            })
        
        for stage in self.session2["stages"]:
            mem = stage.get("memory_total_mb") or stage.get("process", {}).get("memory_rss_mb", 0)
            memory2.append({
                "stage": stage["stage"],
                "memory_mb": mem
            })
        
        # Calculate differences
        differences = []
        for m1, m2 in zip(memory1, memory2):
            if m1["stage"] == m2["stage"]:
                diff = m2["memory_mb"] - m1["memory_mb"]
                differences.append({
                    "stage": m1["stage"],
                    "session1_mb": m1["memory_mb"],
                    "session2_mb": m2["memory_mb"],
                    "diff_mb": round(diff, 2),
                    "diff_percent": round((diff / m1["memory_mb"] * 100) if m1["memory_mb"] > 0 else 0, 1)
                })
        
        return {
            "session1": memory1,
            "session2": memory2,
            "differences": differences
        }
    
    def compare_browser_state(self) -> Dict[str, Any]:
        """Compare browser state at profile page loaded"""
        state1 = None
        state2 = None
        
        for stage in self.session1["stages"]:
            if stage["stage"] == "profile_page_loaded":
                state1 = stage.get("browser_state", {})
                break
        
        for stage in self.session2["stages"]:
            if stage["stage"] == "profile_page_loaded":
                state2 = stage.get("browser_state", {})
                break
        
        if not state1 or not state2:
            return {"error": "Browser state not found"}
        
        # Compare key fields
        differences = []
        
        def compare_nested(path: str, val1: Any, val2: Any):
            if type(val1) != type(val2):
                differences.append({
                    "field": path,
                    "session1": val1,
                    "session2": val2,
                    "type": "type_mismatch"
                })
            elif isinstance(val1, dict):
                for key in set(list(val1.keys()) + list(val2.keys())):
                    compare_nested(f"{path}.{key}", val1.get(key), val2.get(key))
            elif val1 != val2:
                differences.append({
                    "field": path,
                    "session1": val1,
                    "session2": val2,
                    "type": "value_diff"
                })
        
        compare_nested("browser_state", state1, state2)
        
        return {
            "differences": differences,
            "diff_count": len(differences)
        }
    
    def compare_video_state(self) -> Dict[str, Any]:
        """Compare video state when LIVE is playing"""
        video1 = None
        video2 = None
        
        for stage in self.session1["stages"]:
            if stage["stage"] == "live_playing":
                video1 = stage.get("video", {})
                break
        
        for stage in self.session2["stages"]:
            if stage["stage"] == "live_playing":
                video2 = stage.get("video", {})
                break
        
        if not video1 or not video2:
            return {"error": "Video state not found"}
        
        # Compare critical fields
        critical_fields = ["readyState", "paused", "muted", "currentTime"]
        differences = []
        
        for field in critical_fields:
            val1 = video1.get(field)
            val2 = video2.get(field)
            
            if val1 != val2:
                differences.append({
                    "field": field,
                    "session1": val1,
                    "session2": val2
                })
        
        return {
            "session1": video1,
            "session2": video2,
            "differences": differences,
            "critical_diff_count": len(differences)
        }
    
    def identify_first_divergence(self) -> Dict[str, Any]:
        """Identify first stage where sessions diverge"""
        stages1 = self.session1["stages"]
        stages2 = self.session2["stages"]
        
        for i, (s1, s2) in enumerate(zip(stages1, stages2)):
            if s1["stage"] != s2["stage"]:
                return {
                    "divergence_found": True,
                    "stage_number": i + 1,
                    "session1_stage": s1["stage"],
                    "session2_stage": s2["stage"],
                    "note": "Stage names differ"
                }
            
            # Compare memory
            mem1 = s1.get("memory_total_mb") or s1.get("process", {}).get("memory_rss_mb", 0)
            mem2 = s2.get("memory_total_mb") or s2.get("process", {}).get("memory_rss_mb", 0)
            
            if abs(mem1 - mem2) > 50:  # >50MB difference
                return {
                    "divergence_found": True,
                    "stage_number": i + 1,
                    "stage_name": s1["stage"],
                    "session1_memory_mb": mem1,
                    "session2_memory_mb": mem2,
                    "diff_mb": mem2 - mem1,
                    "note": "Significant memory difference (>50MB)"
                }
        
        return {
            "divergence_found": False,
            "note": "No significant divergence found"
        }
    
    def generate_report(self, output_file: str = "baseline_comparison_report.json"):
        """Generate comprehensive comparison report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "session1": {
                "dir": str(self.session1_dir),
                "profile_id": self.session1["stages"][0].get("profile_id") if self.session1["stages"] else None,
                "stage_count": len(self.session1["stages"])
            },
            "session2": {
                "dir": str(self.session2_dir),
                "profile_id": self.session2["stages"][0].get("profile_id") if self.session2["stages"] else None,
                "stage_count": len(self.session2["stages"])
            },
            "chrome_flags": self.compare_chrome_flags(),
            "memory": self.compare_memory(),
            "browser_state": self.compare_browser_state(),
            "video_state": self.compare_video_state(),
            "first_divergence": self.identify_first_divergence()
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[COMPARE] ✅ Report saved: {output_file}")
        return report
    
    def print_summary(self):
        """Print comparison summary"""
        print("\n" + "="*70)
        print("BASELINE COMPARISON SUMMARY")
        print("="*70)
        
        # Chrome flags
        flags_comp = self.compare_chrome_flags()
        if "error" not in flags_comp:
            print(f"\n📋 CHROME FLAGS:")
            print(f"   Session 1: {flags_comp['session1_count']} flags")
            print(f"   Session 2: {flags_comp['session2_count']} flags")
            print(f"   Common: {flags_comp['common_count']} flags")
            print(f"   Only in Session 1: {len(flags_comp['only_in_session1'])} flags")
            print(f"   Only in Session 2: {len(flags_comp['only_in_session2'])} flags")
            
            if flags_comp['only_in_session1']:
                print(f"\n   Flags only in Session 1:")
                for flag in flags_comp['only_in_session1'][:5]:
                    print(f"     - {flag}")
                if len(flags_comp['only_in_session1']) > 5:
                    print(f"     ... and {len(flags_comp['only_in_session1']) - 5} more")
            
            if flags_comp['only_in_session2']:
                print(f"\n   Flags only in Session 2:")
                for flag in flags_comp['only_in_session2'][:5]:
                    print(f"     + {flag}")
                if len(flags_comp['only_in_session2']) > 5:
                    print(f"     ... and {len(flags_comp['only_in_session2']) - 5} more")
        
        # Memory
        mem_comp = self.compare_memory()
        print(f"\n💾 MEMORY COMPARISON:")
        for diff in mem_comp['differences']:
            sign = "+" if diff['diff_mb'] > 0 else ""
            print(f"   {diff['stage']:25} S1: {diff['session1_mb']:6.1f}MB  S2: {diff['session2_mb']:6.1f}MB  Diff: {sign}{diff['diff_mb']:6.1f}MB ({sign}{diff['diff_percent']:5.1f}%)")
        
        # First divergence
        divergence = self.identify_first_divergence()
        print(f"\n🔍 FIRST DIVERGENCE:")
        if divergence['divergence_found']:
            print(f"   Stage: {divergence.get('stage_name', 'N/A')}")
            print(f"   Note: {divergence['note']}")
            if 'diff_mb' in divergence:
                print(f"   Memory diff: {divergence['diff_mb']:.1f}MB")
        else:
            print(f"   {divergence['note']}")
        
        # Video state
        video_comp = self.compare_video_state()
        if "error" not in video_comp:
            print(f"\n🎥 VIDEO STATE:")
            if video_comp['differences']:
                print(f"   Critical differences: {video_comp['critical_diff_count']}")
                for diff in video_comp['differences']:
                    print(f"     {diff['field']}: S1={diff['session1']} vs S2={diff['session2']}")
            else:
                print(f"   ✅ No critical differences")
        
        print("\n" + "="*70)


def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python baseline_compare.py <session1_dir> <session2_dir>")
        print("\nExample:")
        print("  python baseline_compare.py baseline_data/001_20251217_120000 baseline_data/001_20251217_130000")
        sys.exit(1)
    
    session1_dir = Path(sys.argv[1])
    session2_dir = Path(sys.argv[2])
    
    if not session1_dir.exists():
        print(f"❌ Session 1 directory not found: {session1_dir}")
        sys.exit(1)
    
    if not session2_dir.exists():
        print(f"❌ Session 2 directory not found: {session2_dir}")
        sys.exit(1)
    
    # Create comparator
    comparator = BaselineComparator(session1_dir, session2_dir)
    
    # Print summary
    comparator.print_summary()
    
    # Generate report
    output_file = f"comparison_{session1_dir.name}_vs_{session2_dir.name}.json"
    comparator.generate_report(output_file)
    
    print(f"\n✅ Comparison complete!")
    print(f"   Report: {output_file}")


if __name__ == "__main__":
    main()
