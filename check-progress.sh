#!/bin/bash
# Quick sync progress checker

screen -r monerod -X hardcopy /tmp/sync_now.log 2>/dev/null
CURRENT=$(grep "Synced" /tmp/sync_now.log | tail -1 | grep -oP 'Synced \K[0-9]+' | head -1)
TOTAL=3536707

if [ -z "$CURRENT" ]; then
    echo "⚠️  Could not read sync status. Is monerod running?"
    exit 1
fi

PERCENT=$(echo "scale=2; $CURRENT * 100 / $TOTAL" | bc)
REMAINING=$((TOTAL - CURRENT))

# Progress bar
FILLED=$(echo "$PERCENT / 2" | bc)
BAR=$(printf "%-50s" "#" | sed "s/ /#/g" | cut -c1-$FILLED)
EMPTY=$(printf "%-50s" " " | cut -c1-$((50-FILLED)))

echo "╔════════════════════════════════════════════════════════╗"
echo "║        MONERO BLOCKCHAIN SYNC PROGRESS                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "[$BAR$EMPTY] $PERCENT%"
echo ""
echo "Blocks: $CURRENT / $TOTAL"
echo "Remaining: $REMAINING blocks"
echo ""

if [ $(echo "$PERCENT >= 100" | bc) -eq 1 ]; then
    echo "🎉 SYNC COMPLETE! Mining should be active now!"
    echo "   Check dashboard: http://localhost:3380"
elif [ $(echo "$PERCENT >= 50" | bc) -eq 1 ]; then
    echo "⚡ Over halfway there! Getting close!"
elif [ $(echo "$PERCENT >= 25" | bc) -eq 1 ]; then
    echo "📈 Making good progress! Keep going..."
else
    echo "⏳ Early stage - this is the slowest part"
    echo "   Speed increases as you reach newer blocks"
fi

echo ""
echo "Last sync line:"
grep "Synced" /tmp/sync_now.log | tail -1
