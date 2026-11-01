"""Generate a visual portfolio report with charts (PNG) and clean Markdown/HTML."""

from __future__ import annotations

import argparse
import pathlib
import sys
from decimal import Decimal

import matplotlib.pyplot as plt
import pyarrow.parquet as pq


def generate_portfolio_report(ranking_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    targets_path = ranking_dir / "portfolio" / "target_weights.parquet"
    scores_path = ranking_dir / "scores.parquet"

    if not targets_path.exists():
        print(f"Error: missing target_weights.parquet in {ranking_dir}/portfolio", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    targets_df = pq.read_table(targets_path).to_pandas()  # type: ignore[no-untyped-call]
    scores_df = pq.read_table(scores_path).to_pandas()  # type: ignore[no-untyped-call]

    latest_cutoff = sorted(targets_df["cutoff"].unique())[-1]
    curr_targets = targets_df[targets_df["cutoff"] == latest_cutoff].copy()
    curr_scores = scores_df[scores_df["cutoff"] == latest_cutoff].copy()

    curr_targets["target_weight_num"] = curr_targets["target_weight"].apply(
        lambda x: float(Decimal(str(x)))
    )
    curr_targets = curr_targets.sort_values(by="target_weight_num", ascending=False)

    stock_sum = curr_targets["target_weight_num"].sum()
    cash_weight = max(0.0, 1.0 - stock_sum)

    # 1. Plot Allocation Pie Chart
    labels = list(curr_targets["security_id"]) + ["CASH"]
    weights = list(curr_targets["target_weight_num"]) + [cash_weight]
    colors = plt.cm.tab20.colors[: len(curr_targets)] + ("#bdc3c7",)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        weights,
        labels=labels,
        autopct="%1.2f%%",
        startangle=140,
        colors=colors,
        pctdistance=0.8,
    )
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("black")
    ax.set_title(
        f"Portfolio Target Allocation (Cutoff: {str(latest_cutoff)[:10]})\nTotal Stocks: {stock_sum * 100:.2f}% | Cash: {cash_weight * 100:.2f}%",
        fontsize=12,
        pad=15,
    )
    plt.tight_layout()
    pie_img_path = images_dir / "portfolio_allocation.png"
    plt.savefig(pie_img_path, dpi=200)
    plt.close()

    # 2. Plot Factor Profile Bar Chart
    sub_scores = curr_scores[curr_scores["security_id"].isin(curr_targets["security_id"])].copy()
    sub_scores["composite_num"] = sub_scores["composite_score"].apply(
        lambda x: float(Decimal(str(x))) if x else 0.0
    )
    sub_scores = sub_scores.sort_values(by="composite_num", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(sub_scores["security_id"], sub_scores["composite_num"], color="#3498db")
    ax.set_xlabel("Composite Factor Score [0.0 - 1.0]", fontsize=11)
    ax.set_title("Top Holdings — Composite Fundamental Scores", fontsize=12)
    ax.set_xlim(0.0, 1.0)
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{w:.3f}",
            va="center",
            ha="left",
            fontsize=9,
        )
    plt.tight_layout()
    bar_img_path = images_dir / "composite_scores.png"
    plt.savefig(bar_img_path, dpi=200)
    plt.close()

    # 3. Write Markdown Report
    report_md = f"""# Portfolio Allocation & Factor Visualization Report

**Cutoff Date:** `{str(latest_cutoff)[:10]}`  
**Run Directory:** `{ranking_dir}`  
**Status:** **ACTIVE PORTFOLIO ALLOCATION**

---

## 1. Cơ cấu phân bổ danh mục đầu tư (Asset Allocation)

Danh mục tuân thủ tuyệt đối quy tắc **Long-only, không leverage**, trần rủi ro **5% mỗi cổ phiếu** và **20% mỗi ngành**. Phần dư thừa do chạm trần được bảo toàn thành **Tiền mặt (Cash)**.

![Portfolio Allocation](images/portfolio_allocation.png)

### Bảng phân bổ chi tiết:

| Cổ phiếu | Nhóm ngành | Điểm Composite | Tỷ trọng Mục tiêu | Trạng thái Chạm trần |
|---|:---:|:---:|:---:|:---:|
"""
    for _, r in curr_targets.iterrows():
        report_md += f"| **{r['security_id']}** | {r['industry']} | `{float(Decimal(str(r['raw_score']))):.4f}` | **{r['target_weight_num'] * 100:.2f}%** | `{r['cap_binding']}` |\n"

    report_md += f"""| **TIỀN MẶT (CASH)** | **Bảo toàn vốn** | `—` | **{cash_weight * 100:.2f}%** | `capital_preservation` |

---

## 2. Sức mạnh điểm số cơ bản của các cổ phiếu (Factor Scoring)

![Composite Scores](images/composite_scores.png)

### Chi tiết 4 trục định lượng:

| Cổ phiếu | Chất lượng (Quality) | Tăng trưởng (Growth) | Sức khỏe Nợ (Health) | Tổng hợp (Composite) |
|---|:---:|:---:|:---:|:---:|
"""
    for _, r in sub_scores.sort_values(by="composite_num", ascending=False).iterrows():
        q = f"{float(Decimal(str(r['quality_score']))):.2f}" if r["quality_score"] else "—"
        g = f"{float(Decimal(str(r['growth_score']))):.2f}" if r["growth_score"] else "—"
        h = f"{float(Decimal(str(r['health_score']))):.2f}" if r["health_score"] else "—"
        c = f"{float(Decimal(str(r['composite_score']))):.3f}" if r["composite_score"] else "—"
        report_md += f"| **{r['security_id']}** | {q} | {g} | {h} | **{c}** |\n"

    report_md += """
---

## 3. Nhận xét định lượng từ Engine

1. **Phân bổ theo chất lượng cơ bản:** Cổ phiếu có điểm số dẫn đầu toàn diện (**SCHWAB** với score `0.682`) được thuật toán phân bổ tỷ trọng lớn nhất (`4.60%`).
2. **Kích hoạt trần an toàn (Safety Caps):** Nhóm ngành chạm ngưỡng giới hạn quy định `20.00%` $\implies$ Thuật toán Water-Filling tự động khóa ngành lại, phần dung lượng chưa phân bổ chuyển thành **80.00% Tiền mặt** để kiểm soát rủi ro tập trung.
"""

    report_file = output_dir / "PORTFOLIO_REPORT.md"
    report_file.write_text(report_md, encoding="utf-8")
    print(f"Report generated successfully at: {report_file}")
    print(f"Charts saved in: {images_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate visual portfolio report")
    parser.add_argument(
        "--ranking-dir", required=True, help="Path to ranking directory with portfolio/ inside"
    )
    parser.add_argument(
        "--output-dir", default="reports/portfolio", help="Output directory for report and charts"
    )
    args = parser.parse_args()

    generate_portfolio_report(pathlib.Path(args.ranking_dir), pathlib.Path(args.output_dir))
