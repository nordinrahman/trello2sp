#!/usr/bin/env python3
"""Trello to Super Productivity migration tool CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from migrator import TrelloToSPMigrator


def main() -> None:
    """Main entry point for the CLI tool."""
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
