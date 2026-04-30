#!/usr/bin/env python3
"""
MCP 使用报告生成脚本

用法:
    python scripts/usage_report.py                    # 使用默认日志文件
    python scripts/usage_report.py --file usage_log.jsonl
    python scripts/usage_report.py --dir /path/to/logs
    python scripts/usage_report.py --export report.md
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def load_logs(log_file: str) -> list:
    """加载 JSONL 格式的日志文件"""
    entries = []
    if not os.path.exists(log_file):
        print(f"[WARN] 日志文件不存在: {log_file}", file=sys.stderr)
        return entries

    with open(log_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[WARN] 第 {line_num} 行解析失败: {e}", file=sys.stderr)
    return entries


def analyze_logs(entries: list) -> dict:
    """分析日志数据"""
    if not entries:
        return {}

    # 基本统计
    total = len(entries)
    success = sum(1 for e in entries if e.get("success"))
    failed = total - success

    # 工具使用统计
    tool_stats = defaultdict(lambda: {"count": 0, "success": 0, "failed": 0, "durations": []})
    error_stats = defaultdict(int)
    hour_distribution = defaultdict(int)

    for e in entries:
        tool = e.get("tool", "unknown")
        tool_stats[tool]["count"] += 1
        tool_stats[tool]["durations"].append(e.get("duration_ms", 0))

        if e.get("success"):
            tool_stats[tool]["success"] += 1
        else:
            tool_stats[tool]["failed"] += 1
            err_type = e.get("error_type", "unknown")
            error_stats[err_type] += 1

        # 时段分布
        try:
            ts = e.get("timestamp", "")
            if ts:
                hour = datetime.fromisoformat(ts).hour
                hour_distribution[hour] += 1
        except (ValueError, TypeError):
            pass

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "tool_stats": dict(tool_stats),
        "error_stats": dict(error_stats),
        "hour_distribution": dict(hour_distribution),
    }


def generate_text_report(analysis: dict, log_file: str) -> str:
    """生成文本格式报告"""
    import statistics

    lines = []
    lines.append("=" * 70)
    lines.append("金蝶 MCP 使用报告")
    lines.append("=" * 70)
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"日志文件: {log_file}")
    lines.append("")

    if not analysis:
        lines.append("日志为空或解析失败。")
        return "\n".join(lines)

    # 基本统计
    lines.append("-" * 70)
    lines.append("📊 概览")
    lines.append("-" * 70)
    lines.append(f"  总调用次数: {analysis['total']}")
    lines.append(f"  成功/失败: {analysis['success']}/{analysis['failed']}")
    if analysis['total'] > 0:
        rate = analysis['success'] / analysis['total'] * 100
        lines.append(f"  成功率: {rate:.1f}%")
    lines.append("")

    # 工具使用排行
    tool_stats = analysis.get("tool_stats", {})
    if tool_stats:
        lines.append("-" * 70)
        lines.append("🛠️ 工具使用排行 (Top 20)")
        lines.append("-" * 70)
        lines.append(f"  {'工具名称':<45} {'调用次数':>8} {'成功率':>8} {'平均耗时':>10}")
        lines.append("  " + "-" * 75)

        sorted_tools = sorted(
            tool_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:20]

        for tool, stats in sorted_tools:
            count = stats["count"]
            success_rate = stats["success"] / count * 100 if count > 0 else 0
            durations = stats["durations"]
            avg_duration = statistics.mean(durations) if durations else 0
            lines.append(
                f"  {tool:<45} {count:>8} {success_rate:>7.1f}% {avg_duration:>9.0f}ms"
            )
        lines.append("")

    # 错误统计
    error_stats = analysis.get("error_stats", {})
    if error_stats:
        lines.append("-" * 70)
        lines.append("❌ 错误类型分布")
        lines.append("-" * 70)
        sorted_errors = sorted(error_stats.items(), key=lambda x: x[1], reverse=True)
        for err_type, count in sorted_errors:
            lines.append(f"  {err_type}: {count} 次")
        lines.append("")

    # 时段分布
    hour_dist = analysis.get("hour_distribution", {})
    if hour_dist:
        lines.append("-" * 70)
        lines.append("⏰ 使用时段分布")
        lines.append("-" * 70)
        max_count = max(hour_dist.values()) if hour_dist else 1
        for h in range(24):
            count = hour_dist.get(h, 0)
            bar_len = int(count / max_count * 30) if max_count > 0 else 0
            bar = "█" * bar_len
            lines.append(f"  {h:02d}:00 {bar} {count}")
        lines.append("")

    # 改进建议
    lines.append("-" * 70)
    lines.append("💡 改进建议")
    lines.append("-" * 70)

    # 找出使用频率高但成功率低的工具
    suggestions = []
    for tool, stats in tool_stats.items():
        count = stats["count"]
        success_rate = stats["success"] / count if count > 0 else 0
        if count >= 5 and success_rate < 0.7:
            suggestions.append(f"  - {tool}: 成功率仅 {success_rate*100:.1f}%，建议检查参数或 API 可用性")

    # 找出耗时过长的工具
    for tool, stats in tool_stats.items():
        durations = stats["durations"]
        if durations:
            p95 = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
            if p95 > 10000:  # 超过 10 秒
                suggestions.append(f"  - {tool}: P95 耗时 {p95:.0f}ms，建议优化查询条件或分页")

    if suggestions:
        for s in suggestions:
            lines.append(s)
    else:
        lines.append("  暂无明显改进建议")
    lines.append("")

    lines.append("=" * 70)
    lines.append(f"📁 详细日志: {log_file}")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_markdown_report(analysis: dict, log_file: str) -> str:
    """生成 Markdown 格式报告"""
    import statistics

    lines = []
    lines.append("# 金蝶 MCP 使用报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**日志文件**: `{log_file}`")
    lines.append("")

    if not analysis:
        lines.append("日志为空或解析失败。")
        return "\n".join(lines)

    # 概览
    lines.append("## 📊 概览")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总调用次数 | {analysis['total']} |")
    lines.append(f"| 成功 | {analysis['success']} |")
    lines.append(f"| 失败 | {analysis['failed']} |")
    if analysis['total'] > 0:
        rate = analysis['success'] / analysis['total'] * 100
        lines.append(f"| 成功率 | {rate:.1f}% |")
    lines.append("")

    # 工具使用排行
    tool_stats = analysis.get("tool_stats", {})
    if tool_stats:
        lines.append("## 🛠️ 工具使用排行")
        lines.append("")
        lines.append(f"| 工具名称 | 调用次数 | 成功率 | 平均耗时 |")
        lines.append("|----------|----------|--------|----------|")

        sorted_tools = sorted(
            tool_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:20]

        for tool, stats in sorted_tools:
            count = stats["count"]
            success_rate = stats["success"] / count * 100 if count > 0 else 0
            durations = stats["durations"]
            avg_duration = statistics.mean(durations) if durations else 0
            lines.append(f"| {tool} | {count} | {success_rate:.1f}% | {avg_duration:.0f}ms |")
        lines.append("")

    # 错误统计
    error_stats = analysis.get("error_stats", {})
    if error_stats:
        lines.append("## ❌ 错误类型分布")
        lines.append("")
        lines.append(f"| 错误类型 | 次数 |")
        lines.append("|----------|------|")
        sorted_errors = sorted(error_stats.items(), key=lambda x: x[1], reverse=True)
        for err_type, count in sorted_errors:
            lines.append(f"| {err_type} | {count} |")
        lines.append("")

    # 改进建议
    lines.append("## 💡 改进建议")
    lines.append("")

    suggestions = []
    for tool, stats in tool_stats.items():
        count = stats["count"]
        success_rate = stats["success"] / count if count > 0 else 0
        if count >= 5 and success_rate < 0.7:
            suggestions.append(f"- **{tool}**: 成功率仅 {success_rate*100:.1f}%，建议检查参数或 API 可用性")

    for tool, stats in tool_stats.items():
        durations = stats["durations"]
        if durations:
            p95 = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations)
            if p95 > 10000:
                suggestions.append(f"- **{tool}**: P95 耗时 {p95:.0f}ms，建议优化查询条件或分页")

    if suggestions:
        for s in suggestions:
            lines.append(s)
    else:
        lines.append("暂无明显改进建议")
    lines.append("")

    lines.append(f"---")
    lines.append(f"*报告生成时间: {datetime.now().isoformat()}*")

    return "\n".join(lines)


def main():
    # Windows 终端编码处理
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="MCP 使用报告生成工具")
    parser.add_argument("-f", "--file", default="usage_log.jsonl", help="日志文件路径")
    parser.add_argument("-d", "--dir", default=None, help="日志目录（会查找目录下所有 .jsonl 文件）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认打印到标准输出）")
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text", help="输出格式")
    args = parser.parse_args()

    # 确定日志文件
    if args.dir:
        log_files = list(Path(args.dir).glob("*.jsonl"))
        if not log_files:
            print(f"[ERROR] 目录 {args.dir} 中没有找到 .jsonl 文件", file=sys.stderr)
            sys.exit(1)
        # 合并所有日志文件
        all_entries = []
        for lf in log_files:
            all_entries.extend(load_logs(str(lf)))
        log_file_display = f"{args.dir}/*.jsonl ({len(log_files)} files)"
        analysis = analyze_logs(all_entries)
    else:
        log_file = args.file
        entries = load_logs(log_file)
        analysis = analyze_logs(entries)
        log_file_display = log_file

    # 生成报告
    if args.format == "text":
        report = generate_text_report(analysis, log_file_display)
    elif args.format == "markdown":
        report = generate_markdown_report(analysis, log_file_display)
    else:  # json
        report = json.dumps(analysis, ensure_ascii=False, indent=2)

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
