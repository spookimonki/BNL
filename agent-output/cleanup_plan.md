# Phase 0 — Cleanup, Verification & Critique Plan

**Date**: 2026-05-06  
**Workspace**: /home/monki/Desktop/BNL  
**Target**: Pi deployment with SLAM + Nav2 + Exploration

---

## 1. WORKSPACE ANALYSIS STRATEGY

### 1.1 File Inventory

**Current state** (from quick scan):
- 71 Python files
- 23 launch files
- 23 YAML configs
- Multiple test/diagnostic scripts in root

**Categories to identify**:
| Category | Pattern | Action |
|----------|---------|--------|
| ROS2 Packages | `src/*/package.xml` | Keep, verify |
| Launch Files | `*.launch.py` | Verify integration |
| Node Source | `src/*/*.py` | Keep, lint |
| Test Scripts | `*_test.py`, `test_*.py` | Keep if useful |
| Diagnostic Scripts | `*_diagnostic.py` | Keep if documented |
| Standalone Scripts | `*.py` in root | Review, may delete |
| Build Artifacts | `build/`, `install/`, `log/` | Remove (gitignore) |
| Documentation | `*.md` | Keep, update |
| Config Files | `*.yaml` | Verify, consolidate |

### 1.2 Detection Strategy

**For unused files**:
1. Check if file is referenced in any `setup.py` entry_points
2. Check if file is imported by any package
3. Check if file is called from any launch file
4. Check git history (last modified date)
5. Check if file has duplicate functionality

**For verification without hardware**:
1. Static analysis: imports, dependencies
2. Launch file tracing: does node get launched?
3. Config validation: YAML syntax, parameter completeness
4. TF tree analysis: are all frames connected?
5. Topic graph analysis: do publishers/subscribers match?

---

## 2. VERIFICATION APPROACH

### 2.1 What Can Be Verified (No Hardware)

| Verification Type | Method | Confidence |
|-------------------|--------|------------|
| Code syntax | `python3 -m py_compile` | 100% |
| Import resolution | Check all imports resolve | 95% |
| Launch file validity | Parse launch files | 95% |
| YAML syntax | `yaml.safe_load()` | 100% |
| TF tree completeness | Analyze static transforms | 90% |
| Topic name consistency | Grep for topic strings | 80% |
| Parameter usage | Check param declarations | 85% |

### 2.2 What Cannot Be Verified

| Item | Reason |
|------|--------|
| GPIO functionality | No Pi hardware |
| UART communication | No LiDAR connected |
| I2C communication | No IMU connected |
| Motor control | No H-bridge connected |
| Actual SLAM performance | No runtime test |
| Odometry accuracy | No robot motion |

**Strategy**: Mark these as `THEORETICALLY VALID` vs `VERIFIED`

---

## 3. CRITIQUE FRAMEWORK

### 3.1 ROS2 Best Practices Checklist

Based on REP standards and Nav2 documentation:

**REP-105 (Coordinate Frames)**:
- [ ] `map` → `odom` → `base_link` chain exists
- [ ] Sensor frames (`lidar_link`, `imu_link`) attached to `base_link`
- [ ] Transforms use correct conventions (REP-103)

**REP-103 (Standard Units)**:
- [ ] Distances in meters
- [ ] Angles in radians
- [ ] Time in seconds

**Nav2 Requirements**:
- [ ] `/cmd_vel` subscriber in motor node
- [ ] `/scan` publisher for costmaps
- [ ] `/odom` or `/odom/calibrated` for localization
- [ ] TF tree complete for costmap transformation

**SLAM Requirements** (slam_toolbox):
- [ ] `/scan` topic (LaserScan)
- [ ] `/tf` with `odom` → `base_link`
- [ ] Static transforms for sensors

### 3.2 Common Failure Patterns to Detect

| Pattern | Symptom | Detection |
|---------|---------|-----------|
| Missing TF | Costmap errors | Check `view_frames.py` output |
| Wrong frame_id | TF warnings | Grep `frame_id` in code |
| Topic mismatch | No data | Check topic names match |
| Hardcoded paths | FileNotFound | Grep `/home/` |
| Blocking I/O | Node hangs | Check for `time.sleep()` in callbacks |
| Thread-unsafe GPIO | Crashes | Check GPIO in callbacks |
| Timestamp assumptions | Sync issues | Check time handling |

---

## 4. DELETION SAFETY PROTOCOL

### 4.1 Classification System

| Category | Criteria | Action |
|----------|----------|--------|
| **ACTIVE** | Referenced in launch/setup.py | KEEP |
| **DOCUMENTATION** | `.md`, `.txt` files | KEEP (update) |
| **TEST** | Test scripts with valid tests | KEEP |
| **DIAGNOSTIC** | Debug tools, may be useful | KEEP (mark) |
| **DUPLICATE** | Same functionality elsewhere | DELETE |
| **ORPHAN** | No references, unclear purpose | MARK (unknown) |
| **ARTIFACT** | `build/`, `log/`, `.pyc` | DELETE |

### 4.2 Pre-Deletion Checks

Before deleting any file:
1. [ ] Check if imported anywhere: `grep -r "import X"`
2. [ ] Check if launched anywhere: `grep -r "executable="`
3. [ ] Check git log for recent changes
4. [ ] Check if file has unique functionality
5. [ ] If uncertain → MOVE to `unused/` instead of delete

### 4.3 Files Likely Safe to Delete

| File | Reason |
|------|--------|
| `System" : true,` | Malformed filename, 0 bytes |
| `test.txt`, `test2.txt` | Empty/test files |
| `frames_*.gv`, `frames_*.pdf` | Old TF diagrams |
| `build/`, `install/`, `log/` | Build artifacts |
| `agent-output/backups/` | Old backups |

### 4.4 Files Requiring Review

| File | Concern |
|------|---------|
| `explore.py` | Used? Or replaced by frontier exploration? |
| `random_move.py` | Demo or useful? |
| `bno085_*.py` | Replaced by `imuodom.py`? |
| `encoder_test*.py` | Replaced by `wheelodom.py`? |
| `servo_smooth.py` | Replaced by `servo_oscillator.py`? |

---

## 5. EXECUTION PLAN

### Phase 0: Plan (Current)
- Create this plan
- Critique for gaps

### Phase 1: Verification
- Inventory all packages
- Trace launch → node → source
- Check dependencies
- Output: `verification_report.md`

### Phase 1.5: Safety Check
- Classify files (safe/probably/unknown)
- Output: classification list

### Phase 2: Critique
- Review sensor pipeline
- Review state estimation
- Review SLAM/Nav2 setup
- Review exploration
- Output: `critique_report.md`

### Phase 2.5: Apply Fixes
- Fix high-confidence issues
- Do NOT implement complex new features

### Phase 3: Cleanup
- Remove artifacts
- Remove confirmed unused
- Organize structure
- Log all changes

### Phase 4: README
- System architecture
- Setup instructions
- Known issues
- Limitations

### Phase 5: Git Prep
- Update `.gitignore`
- Clean build artifacts
- Suggest commit message

---

## 6. CRITIQUE OF THIS PLAN

### Potential Weaknesses

1. **May delete useful test files**:
   - Test scripts might be used for debugging
   - Mitigation: Move to `tools/` instead of delete

2. **Cannot verify runtime behavior**:
   - All analysis is static
   - Mitigation: Mark runtime claims as `THEORETICAL`

3. **May miss cross-file dependencies**:
   - Dynamic imports not detected
   - Mitigation: Check `importlib` usage

4. **Critique may be too harsh**:
   - Student projects ≠ production systems
   - Mitigation: Distinguish "must fix" vs "nice to have"

### Where I Could Be Wrong

| Assumption | Risk | Mitigation |
|------------|------|------------|
| "Test files unused" | May need for debugging | Keep in `tools/` |
| "Old diagnostics replaced" | New code may have bugs | Keep both, mark |
| "Build artifacts safe" | May have custom configs | Check contents first |

---

## 7. SUCCESS CRITERIA

Phase 0 plan complete when:
- [ ] Deletion safety protocol defined
- [ ] Verification methods documented
- [ ] Critique framework established
- [ ] Execution timeline clear

**Proceeding to Phase 1: Verification**
