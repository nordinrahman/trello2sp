#!/usr/bin/env python3
"""Trello to Super Productivity migration tool.

Transforms a Trello board export into a Super Productivity project
and merges it into an existing SP export JSON.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class TrelloToSPMigrator:
    """Handles migration from Trello to Super Productivity."""
    
    def __init__(
        self,
        trello_file: Path,
        sp_export_file: Path,
        project_title: str | None = None,
        include_archived: bool = False,
        member_tags: bool = False,
        list_tags: bool = True,
        label_tags: bool = True,
        reuse_project: bool = False,
    ) -> None:
        """Initialize the migrator.
        
        Args:
            trello_file: Path to Trello board export JSON
            sp_export_file: Path to Super Productivity export JSON
            project_title: Custom title for the new project
            include_archived: Whether to include archived cards
            member_tags: Whether to create tags for Trello members
            list_tags: Whether to create tags for Trello lists
            label_tags: Whether to create tags for Trello labels
            reuse_project: Whether to merge into existing project with same title
        """
        self.trello_file = trello_file
        self.sp_export_file = sp_export_file
        self.project_title = project_title
        self.include_archived = include_archived
        self.member_tags = member_tags
        self.list_tags = list_tags
        self.label_tags = label_tags
        self.reuse_project = reuse_project
        
        # Internal state
        self.trello_data: Dict[str, Any] = {}
        self.sp_data: Dict[str, Any] = {}
        self.new_project_id: str = ""
        self.tag_title_to_id: Dict[str, str] = {}
        self.task_ids: Set[str] = set()
        self.subtask_ids: Set[str] = set()
        
    def load_data(self) -> None:
        """Load input JSON files."""
        self.trello_data = self._load_json(self.trello_file)
        self.sp_data = self._load_json(self.sp_export_file)
        
        # Handle SP data structure - actual data is under "data" key
        if "data" in self.sp_data:
            self.sp_data = self.sp_data["data"]
        
    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling."""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
            
    def migrate(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform the migration.
        
        Returns:
            Tuple of (delta_data, merged_data)
        """
        self.load_data()
        
        # Initialize tag mapping from existing SP data
        self._initialize_tag_mapping()
        
        # Create tags first (needed for tasks)
        tags_data = self._create_tags()
        
        # Create tasks and subtasks
        tasks_data = self._create_tasks()
        
        # Create project with task IDs
        project_data = self._create_project(list(tasks_data.get("ids", [])))
        
        # Build delta (just the new project data)
        delta_data = {
            "project": project_data,
            "tag": tags_data,
            "task": tasks_data,
        }
        
        # Merge into existing SP data
        merged_data = self._merge_into_sp_export(delta_data)
        
        return delta_data, merged_data
        
    def _initialize_tag_mapping(self) -> None:
        """Initialize tag title to ID mapping from existing SP data."""
        tag_entities = self.sp_data.get("tag", {}).get("entities", {})
        for tag_id, tag in tag_entities.items():
            title = tag.get("title", "")
            if title:
                self.tag_title_to_id[title] = tag_id
                
    def _create_project(self, task_ids: List[str]) -> Dict[str, Any]:
        """Create a new SP project from Trello board."""
        board_name = self.trello_data.get("name", "Trello Board")
        project_title = self.project_title or f"Imported from Trello: {board_name}"
        
        # Check if project with same title exists
        existing_project_id = self._find_existing_project(project_title)
        
        if existing_project_id and not self.reuse_project:
            project_title += " (Trello)"
            
        # Generate new project ID
        self.new_project_id = str(uuid.uuid4())
        
        # Create new project entity
        project_entity = {
            "id": self.new_project_id,
            "title": project_title,
            "created": datetime.now().timestamp() * 1000,
            "taskIds": task_ids,  # Include the task IDs
            "color": None,
            "icon": None,
            "defaultTags": [],
            "backlogTaskIds": [],
            "noteIds": [],
            "advancedCfg": {},
            "theme": {},
            "isHiddenFromMenu": False,
            "isArchived": False,
            "isEnableBacklog": False,
        }
        
        # Return just the new project data
        return {
            "ids": [self.new_project_id],
            "entities": {self.new_project_id: project_entity},
        }
        
    def _find_existing_project(self, title: str) -> str | None:
        """Find existing project ID by title."""
        project_entities = self.sp_data.get("project", {}).get("entities", {})
        for project_id, project in project_entities.items():
            if project.get("title") == title:
                return project_id
        return None
        
    def _create_tags(self) -> Dict[str, Any]:
        """Create tags for lists, labels, and optionally members."""
        tag_ids = set()
        tag_entities = {}
        
        # Create list tags
        if self.list_tags:
            for trello_list in self.trello_data.get("lists", []):
                list_name = trello_list.get("name", "").strip()
                if not list_name or trello_list.get("closed", False):
                    continue
                    
                tag_title = f"list:{list_name}"
                tag_id = self._get_or_create_tag(
                    tag_title, tag_ids, tag_entities
                )
                
        # Create label tags
        if self.label_tags:
            for label in self.trello_data.get("labels", []):
                label_name = label.get("name", "").strip()
                if not label_name:
                    continue
                    
                tag_id = self._get_or_create_tag(
                    label_name, tag_ids, tag_entities
                )
                
        # Create member tags
        if self.member_tags:
            for member in self.trello_data.get("members", []):
                member_name = member.get("fullName", "").strip() or member.get("username", "").strip()
                if not member_name:
                    continue
                    
                tag_title = f"@member:{member_name}"
                tag_id = self._get_or_create_tag(
                    tag_title, tag_ids, tag_entities
                )
                
        # Return just the new tags
        return {
            "ids": list(tag_ids),
            "entities": tag_entities,
        }
        
    def _get_or_create_tag(
        self,
        title: str,
        new_ids: Set[str],
        new_entities: Dict[str, Any],
    ) -> str:
        """Get existing tag ID or create new tag."""
        # Check if tag already exists
        if title in self.tag_title_to_id:
            return self.tag_title_to_id[title]
            
        # Create new tag
        tag_id = str(uuid.uuid4())
        new_ids.add(tag_id)
        new_entities[tag_id] = {
            "id": tag_id,
            "title": title,
            "created": datetime.now().timestamp() * 1000,
            "taskIds": [],
            "color": None,
            "advancedCfg": {},
            "theme": {},
        }
        
        # Update mapping
        self.tag_title_to_id[title] = tag_id
        
        return tag_id
        
    def _create_tasks(self) -> Dict[str, Any]:
        """Create tasks and subtasks from Trello cards."""
        task_ids = set()
        task_entities = {}
        
        # Process each card
        for card in self.trello_data.get("cards", []):
            # Skip archived cards unless requested
            if card.get("closed", False) and not self.include_archived:
                continue
                
            task_data = self._create_task_from_card(card)
            if task_data:
                task_id = task_data["id"]
                task_ids.add(task_id)
                task_entities[task_id] = task_data
                self.task_ids.add(task_id)
                
                # Create subtasks from checklists
                subtask_entities = self._create_subtasks_from_checklists(card, task_id)
                task_entities.update(subtask_entities)
                
        # Return just the new tasks
        return {
            "ids": list(task_ids),
            "entities": task_entities,
        }
        
    def _create_task_from_card(self, card: Dict[str, Any]) -> Dict[str, Any] | None:
        """Create a SP task from a Trello card."""
        title = card.get("name", "").strip()
        if not title:
            return None
            
        # Collect tag IDs
        tag_ids = []
        
        # Add list tag
        if self.list_tags:
            list_id = card.get("idList")
            list_name = self._get_list_name(list_id)
            if list_name:
                list_tag_title = f"list:{list_name}"
                if list_tag_title in self.tag_title_to_id:
                    tag_ids.append(self.tag_title_to_id[list_tag_title])
                    
        # Add label tags
        if self.label_tags:
            for label_id in card.get("idLabels", []):
                label_name = self._get_label_name(label_id)
                if label_name and label_name in self.tag_title_to_id:
                    tag_ids.append(self.tag_title_to_id[label_name])
                    
        # Add member tags
        if self.member_tags:
            for member_id in card.get("idMembers", []):
                member_name = self._get_member_name(member_id)
                if member_name:
                    member_tag_title = f"@member:{member_name}"
                    if member_tag_title in self.tag_title_to_id:
                        tag_ids.append(self.tag_title_to_id[member_tag_title])
                        
        # Convert due date
        due_day = None
        if card.get("due"):
            try:
                due_dt = datetime.fromisoformat(card["due"].replace('Z', '+00:00'))
                due_day = due_dt.strftime("%Y-%m-%d")
            except ValueError:
                pass  # Skip invalid dates
                
        # Build notes
        notes = card.get("desc", "").strip()
        card_url = card.get("url", "").strip()
        if card_url:
            notes += f"\nTrello URL: {card_url}" if notes else f"Trello URL: {card_url}"
            
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            "notes": notes,
            "dueDay": due_day,
            "tagIds": tag_ids,
            "projectId": self.new_project_id,
            "isDone": card.get("closed", False) and self.include_archived,
            "created": datetime.now().timestamp() * 1000,
            "timeSpent": 0,
            "timeEstimate": 0,
            "subTaskIds": [],
            "attachments": [],
            "timeSpentOnDay": {},
        }
        
    def _create_subtasks_from_checklists(self, card: Dict[str, Any], parent_task_id: str) -> Dict[str, Any]:
        """Create subtasks from Trello checklist items."""
        subtask_entities = {}
        subtask_ids = []
        
        for checklist in card.get("checklists", []):
            for check_item in checklist.get("checkItems", []):
                item_name = check_item.get("name", "").strip()
                if not item_name:
                    continue
                    
                subtask_id = str(uuid.uuid4())
                subtask_ids.append(subtask_id)
                self.subtask_ids.add(subtask_id)
                
                subtask_entities[subtask_id] = {
                    "id": subtask_id,
                    "title": item_name,
                    "parentId": parent_task_id,
                    "isDone": check_item.get("state", "incomplete") == "complete",
                    "created": datetime.now().timestamp() * 1000,
                    "timeSpent": 0,
                    "timeEstimate": 0,
                }
                
        # Update parent task with subtask IDs
        if subtask_ids:
            # This will be handled when we merge back to the main task entities
            pass
            
        return subtask_entities
        
    def _get_list_name(self, list_id: str) -> str | None:
        """Get list name by ID."""
        for trello_list in self.trello_data.get("lists", []):
            if trello_list.get("id") == list_id:
                return trello_list.get("name", "").strip()
        return None
        
    def _get_label_name(self, label_id: str) -> str | None:
        """Get label name by ID."""
        for label in self.trello_data.get("labels", []):
            if label.get("id") == label_id:
                return label.get("name", "").strip()
        return None
        
    def _get_member_name(self, member_id: str) -> str | None:
        """Get member name by ID."""
        for member in self.trello_data.get("members", []):
            if member.get("id") == member_id:
                return (member.get("fullName", "").strip() or 
                       member.get("username", "").strip())
        return None
        
    def _merge_into_sp_export(self, delta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge delta data into existing SP export."""
        merged = self.sp_data.copy()
        
        # Sections that use the ids/entities structure (can be merged)
        mergeable_sections = ["task", "project", "tag", "note", "issueProvider", "metric", "simpleCounter", "taskRepeatCfg"]
        
        # Sections that should preserve original format (copy as-is)
        preserve_sections = ["planner", "boards", "menuTree", "timeTracking", "pluginUserData", "pluginMetadata", "reminders", "archiveYoung", "archiveOld", "globalConfig"]
        
        # Merge sections that use ids/entities structure
        for slice_name, slice_data in delta_data.items():
            if slice_name in mergeable_sections:
                if slice_name in merged:
                    # Merge existing slice
                    existing_slice = merged[slice_name]
                    merged[slice_name] = {
                        "ids": list(set(existing_slice.get("ids", [])).union(set(slice_data.get("ids", [])))),
                        "entities": {**existing_slice.get("entities", {}), **slice_data.get("entities", {})},
                    }
                else:
                    # Add new slice
                    merged[slice_name] = slice_data
        
        # Preserve sections that should keep original format
        for section in preserve_sections:
            if section in self.sp_data:
                merged[section] = self.sp_data[section]
        
        # Ensure task section has required fields
        if "task" in merged:
            task_section = merged["task"]
            if "currentTaskId" not in task_section:
                task_section["currentTaskId"] = None
            if "selectedTaskId" not in task_section:
                task_section["selectedTaskId"] = None
            if "taskDetailTargetPanel" not in task_section:
                task_section["taskDetailTargetPanel"] = None
            if "lastCurrentTaskId" not in task_section:
                task_section["lastCurrentTaskId"] = None
            if "isDataLoaded" not in task_section:
                task_section["isDataLoaded"] = False
                
        # Update parent tasks with subtask IDs
        self._update_parent_subtask_ids(merged)
        
        return merged
        
    def _update_parent_subtask_ids(self, merged_data: Dict[str, Any]) -> None:
        """Update parent tasks with subtask IDs."""
        task_entities = merged_data.get("task", {}).get("entities", {})
        
        for task_id, task in task_entities.items():
            if task_id in self.task_ids:  # Only update new tasks
                subtask_ids = [
                    sub_id for sub_id, subtask in task_entities.items()
                    if subtask.get("parentId") == task_id
                ]
                task["subTaskIds"] = subtask_ids
                
    def save_outputs(self, delta_data: Dict[str, Any], merged_data: Dict[str, Any], 
                     out_delta: Path, out_merged: Path) -> None:
        """Save output files."""
        # Create output directories
        out_delta.parent.mkdir(parents=True, exist_ok=True)
        out_merged.parent.mkdir(parents=True, exist_ok=True)
        
        # Save delta file (just the new project data)
        self._save_json(delta_data, out_delta)
        
        # Save merged file with SP wrapper structure
        # Load original SP file to preserve wrapper metadata
        original_sp = self._load_json(self.sp_export_file)
        if "data" in original_sp:
            # Preserve wrapper metadata but update data
            merged_with_wrapper = original_sp.copy()
            merged_with_wrapper["data"] = merged_data
            merged_with_wrapper["timestamp"] = datetime.now().timestamp() * 1000
            merged_with_wrapper["lastUpdate"] = datetime.now().timestamp() * 1000
            self._save_json(merged_with_wrapper, out_merged)
        else:
            # Fallback - save as-is
            self._save_json(merged_data, out_merged)
        
    def _save_json(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save data to JSON file."""
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def print_summary(self, delta_data: Dict[str, Any]) -> None:
        """Print migration summary."""
        projects_added = len(delta_data.get("project", {}).get("ids", []))
        tasks_added = len([tid for tid in delta_data.get("task", {}).get("ids", []) 
                          if tid in self.task_ids])
        subtasks_added = len(self.subtask_ids)
        
        # Count new vs reused tags
        existing_tag_count = len(self.sp_data.get("tag", {}).get("ids", []))
        total_tag_count = len(delta_data.get("tag", {}).get("ids", []))
        new_tags = total_tag_count - existing_tag_count
        reused_tags = existing_tag_count if total_tag_count > existing_tag_count else 0
        
        print(f"Migration summary:")
        print(f"  Projects added: {projects_added}")
        print(f"  Tasks added:    {tasks_added}")
        print(f"  Subtasks added: {subtasks_added}")
        print(f"  Tags created:   {new_tags} (reused: {reused_tags})")
        
    def validate_data(self, data: Dict[str, Any]) -> None:
        """Validate the migrated data."""
        # Check required structure
        required_slices = ["project", "tag", "task"]
        for slice_name in required_slices:
            if slice_name not in data:
                raise ValueError(f"Missing required slice: {slice_name}")
                
        # Validate project
        project_slice = data["project"]
        if not project_slice.get("ids") or not project_slice.get("entities"):
            raise ValueError("Invalid project slice structure")
            
        # Validate tasks
        task_slice = data["task"]
        task_entities = task_slice.get("entities", {})
        
        for task_id, task in task_entities.items():
            # Check required fields
            required_fields = ["id", "title", "projectId", "created", "tagIds", 
                             "subTaskIds", "isDone", "timeSpent", "timeEstimate"]
            for field in required_fields:
                if field not in task:
                    raise ValueError(f"Task {task_id} missing required field: {field}")
                    
            # Check subtask references
            for subtask_id in task.get("subTaskIds", []):
                if subtask_id not in task_entities:
                    raise ValueError(f"Task {task_id} references non-existent subtask: {subtask_id}")
                    
        print("Data validation passed")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate Trello board to Super Productivity project"
    )
    
    parser.add_argument("--trello", required=True, type=Path,
                       help="Path to Trello board export JSON")
    parser.add_argument("--sp-export", required=True, type=Path, dest="sp_export",
                       help="Path to Super Productivity export JSON")
    parser.add_argument("--out-delta", required=True, type=Path, dest="out_delta",
                       help="Path for output delta JSON")
    parser.add_argument("--out-merged", required=True, type=Path, dest="out_merged",
                       help="Path for output merged JSON")
    parser.add_argument("--project-title", type=str, dest="project_title",
                       help="Custom title for the new project")
    parser.add_argument("--include-archived", action="store_true", dest="include_archived",
                       help="Include archived cards")
    parser.add_argument("--member-tags", action="store_true", dest="member_tags",
                       help="Create tags for Trello members")
    parser.add_argument("--list-tags", action="store_true", default=True, dest="list_tags",
                       help="Create tags for Trello lists")
    parser.add_argument("--no-list-tags", action="store_false", dest="list_tags",
                       help="Do not create tags for Trello lists")
    parser.add_argument("--label-tags", action="store_true", default=True, dest="label_tags",
                       help="Create tags for Trello labels")
    parser.add_argument("--no-label-tags", action="store_false", dest="label_tags",
                       help="Do not create tags for Trello labels")
    parser.add_argument("--reuse-project", action="store_true", dest="reuse_project",
                       help="Merge into existing project with same title")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                       help="Run without writing files")
    
    args = parser.parse_args()
    
    # Create migrator
    migrator = TrelloToSPMigrator(
        trello_file=args.trello,
        sp_export_file=args.sp_export,
        project_title=args.project_title,
        include_archived=args.include_archived,
        member_tags=args.member_tags,
        list_tags=args.list_tags,
        label_tags=args.label_tags,
        reuse_project=args.reuse_project,
    )
    
    try:
        # Perform migration
        delta_data, merged_data = migrator.migrate()
        
        # Validate data
        migrator.validate_data(merged_data)
        
        # Print summary
        migrator.print_summary(delta_data)
        
        if not args.dry_run:
            # Save outputs
            migrator.save_outputs(delta_data, merged_data, args.out_delta, args.out_merged)
            print(f"Output files: {args.out_delta}, {args.out_merged}")
        else:
            print("Dry run completed - no files written")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
