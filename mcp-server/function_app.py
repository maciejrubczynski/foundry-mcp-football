"""
MCP Server for Football (Soccer) Statistics
Deployed as Azure Functions with MCP extension bindings.

Tools:
  - search_players: Search for football players
  - get_player_stats: Get detailed stats for a player
  - compare_players: Compare two players side-by-side
"""

import logging
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ─── In-memory football database ────────────────────────────────────────────
PLAYERS = {
    "lewandowski": {
        "id": "lew9",
        "name": "Robert Lewandowski",
        "nationality": "Poland",
        "position": "Striker",
        "club": "FC Barcelona",
        "age": 37,
        "stats": {
            "season": "2025/26",
            "appearances": 28,
            "goals": 19,
            "assists": 5,
            "minutes_played": 2340,
            "goals_per_90": 0.73,
            "shots_on_target_pct": 52.1,
            "pass_accuracy": 81.3,
            "career_goals": 672,
            "career_assists": 171,
        },
    },
    "mbappe": {
        "id": "mba7",
        "name": "Kylian Mbappé",
        "nationality": "France",
        "position": "Forward",
        "club": "Real Madrid",
        "age": 27,
        "stats": {
            "season": "2025/26",
            "appearances": 30,
            "goals": 22,
            "assists": 8,
            "minutes_played": 2610,
            "goals_per_90": 0.76,
            "shots_on_target_pct": 48.7,
            "pass_accuracy": 84.1,
            "career_goals": 358,
            "career_assists": 132,
        },
    },
    "haaland": {
        "id": "haa9",
        "name": "Erling Haaland",
        "nationality": "Norway",
        "position": "Striker",
        "club": "Manchester City",
        "age": 25,
        "stats": {
            "season": "2025/26",
            "appearances": 29,
            "goals": 27,
            "assists": 4,
            "minutes_played": 2505,
            "goals_per_90": 0.97,
            "shots_on_target_pct": 55.3,
            "pass_accuracy": 76.8,
            "career_goals": 295,
            "career_assists": 58,
        },
    },
    "vinicius": {
        "id": "vin7",
        "name": "Vinícius Júnior",
        "nationality": "Brazil",
        "position": "Winger",
        "club": "Real Madrid",
        "age": 25,
        "stats": {
            "season": "2025/26",
            "appearances": 27,
            "goals": 15,
            "assists": 12,
            "minutes_played": 2295,
            "goals_per_90": 0.59,
            "shots_on_target_pct": 44.2,
            "pass_accuracy": 82.5,
            "career_goals": 128,
            "career_assists": 89,
        },
    },
    "salah": {
        "id": "sal11",
        "name": "Mohamed Salah",
        "nationality": "Egypt",
        "position": "Forward",
        "club": "Liverpool",
        "age": 33,
        "stats": {
            "season": "2025/26",
            "appearances": 31,
            "goals": 21,
            "assists": 14,
            "minutes_played": 2700,
            "goals_per_90": 0.70,
            "shots_on_target_pct": 46.8,
            "pass_accuracy": 80.9,
            "career_goals": 372,
            "career_assists": 178,
        },
    },
    "bellingham": {
        "id": "bel5",
        "name": "Jude Bellingham",
        "nationality": "England",
        "position": "Midfielder",
        "club": "Real Madrid",
        "age": 22,
        "stats": {
            "season": "2025/26",
            "appearances": 30,
            "goals": 12,
            "assists": 9,
            "minutes_played": 2610,
            "goals_per_90": 0.41,
            "shots_on_target_pct": 42.1,
            "pass_accuracy": 89.3,
            "career_goals": 78,
            "career_assists": 52,
        },
    },
    "yamal": {
        "id": "yam19",
        "name": "Lamine Yamal",
        "nationality": "Spain",
        "position": "Winger",
        "club": "FC Barcelona",
        "age": 18,
        "stats": {
            "season": "2025/26",
            "appearances": 29,
            "goals": 10,
            "assists": 15,
            "minutes_played": 2320,
            "goals_per_90": 0.39,
            "shots_on_target_pct": 41.5,
            "pass_accuracy": 85.7,
            "career_goals": 24,
            "career_assists": 31,
        },
    },
    "szczesny": {
        "id": "szc1",
        "name": "Wojciech Szczęsny",
        "nationality": "Poland",
        "position": "Goalkeeper",
        "club": "FC Barcelona",
        "age": 36,
        "stats": {
            "season": "2025/26",
            "appearances": 20,
            "goals": 0,
            "assists": 0,
            "minutes_played": 1800,
            "clean_sheets": 9,
            "saves_per_90": 3.2,
            "save_percentage": 74.5,
            "career_goals": 0,
            "career_assists": 0,
        },
    },
}


def _find_players(query: str) -> list[dict]:
    """Search players by name, nationality, position, or club."""
    query_lower = query.lower()
    results = []
    for key, player in PLAYERS.items():
        if (
            query_lower in player["name"].lower()
            or query_lower in player["nationality"].lower()
            or query_lower in player["position"].lower()
            or query_lower in player["club"].lower()
            or query_lower in key
        ):
            results.append(player)
    return results


def _get_player_by_name(name: str):
    """Get a player by partial name match."""
    matches = _find_players(name)
    return matches[0] if matches else None


# ─── MCP Tools (Azure Functions MCP extension) ──────────────────────────────


@app.mcp_tool()
@app.mcp_tool_property(
    arg_name="query",
    description="Search term: player name, country, position, or club name.",
)
def search_players(query: str) -> str:
    """Search for football players by name, nationality, position, or club."""
    logging.info(f"search_players called with query: {query}")
    results = _find_players(query)
    if not results:
        return f"No players found matching '{query}'. Try: Lewandowski, Poland, Striker, Barcelona."

    lines = [f"Found {len(results)} player(s) matching '{query}':\n"]
    for p in results:
        lines.append(
            f"  - {p['name']} | {p['position']} | {p['club']} | "
            f"{p['nationality']} | Age {p['age']}"
        )
    return "\n".join(lines)


@app.mcp_tool()
@app.mcp_tool_property(
    arg_name="player_name",
    description="Full or partial player name (e.g. 'Haaland', 'Lewandowski').",
)
def get_player_stats(player_name: str) -> str:
    """Get detailed season and career statistics for a specific football player."""
    logging.info(f"get_player_stats called for: {player_name}")
    p = _get_player_by_name(player_name)
    if not p:
        return f"Player '{player_name}' not found. Use search_players first."

    s = p["stats"]
    lines = [
        f"Player: {p['name']} — {p['position']}",
        f"Club: {p['club']} | Nationality: {p['nationality']} | Age: {p['age']}",
        f"",
        f"Season {s['season']}:",
        f"  Appearances: {s['appearances']}",
        f"  Goals: {s['goals']}",
        f"  Assists: {s['assists']}",
        f"  Minutes: {s['minutes_played']}",
    ]

    if p["position"] == "Goalkeeper":
        lines.extend([
            f"  Clean Sheets: {s.get('clean_sheets', 'N/A')}",
            f"  Saves/90: {s.get('saves_per_90', 'N/A')}",
            f"  Save %: {s.get('save_percentage', 'N/A')}%",
        ])
    else:
        lines.extend([
            f"  Goals/90: {s['goals_per_90']}",
            f"  Shots on Target: {s['shots_on_target_pct']}%",
            f"  Pass Accuracy: {s['pass_accuracy']}%",
        ])

    lines.extend([
        f"",
        f"Career Totals:",
        f"  Goals: {s['career_goals']}",
        f"  Assists: {s['career_assists']}",
    ])

    return "\n".join(lines)


@app.mcp_tool()
@app.mcp_tool_property(
    arg_name="player1_name",
    description="First player name (e.g. 'Haaland').",
)
@app.mcp_tool_property(
    arg_name="player2_name",
    description="Second player name (e.g. 'Mbappe').",
)
def compare_players(player1_name: str, player2_name: str) -> str:
    """Compare statistics of two football players side-by-side."""
    logging.info(f"compare_players: {player1_name} vs {player2_name}")
    p1 = _get_player_by_name(player1_name)
    p2 = _get_player_by_name(player2_name)

    if not p1:
        return f"Player '{player1_name}' not found."
    if not p2:
        return f"Player '{player2_name}' not found."

    s1, s2 = p1["stats"], p2["stats"]

    lines = [
        f"Head-to-Head: {p1['name']} vs {p2['name']}",
        f"{'='*55}",
        f"{'Metric':<22} {p1['name']:<16} {p2['name']:<16}",
        f"{'-'*55}",
        f"{'Club':<22} {p1['club']:<16} {p2['club']:<16}",
        f"{'Age':<22} {str(p1['age']):<16} {str(p2['age']):<16}",
        f"{'Appearances':<22} {str(s1['appearances']):<16} {str(s2['appearances']):<16}",
        f"{'Goals':<22} {str(s1['goals']):<16} {str(s2['goals']):<16}",
        f"{'Assists':<22} {str(s1['assists']):<16} {str(s2['assists']):<16}",
        f"{'Minutes':<22} {str(s1['minutes_played']):<16} {str(s2['minutes_played']):<16}",
    ]

    if p1["position"] != "Goalkeeper" and p2["position"] != "Goalkeeper":
        lines.append(
            f"{'Goals/90':<22} {str(s1.get('goals_per_90','N/A')):<16} {str(s2.get('goals_per_90','N/A')):<16}"
        )

    lines.extend([
        f"{'Career Goals':<22} {str(s1['career_goals']):<16} {str(s2['career_goals']):<16}",
        f"{'Career Assists':<22} {str(s1['career_assists']):<16} {str(s2['career_assists']):<16}",
    ])

    return "\n".join(lines)
