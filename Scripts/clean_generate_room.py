"""Find (and optionally delete) nodes in BP_RoomGenerator.GenerateRoom that no longer do anything."""
import unreal, sys
DELETE = True
L = unreal.BlueprintEditorLibrary; PL = unreal.BlueprintGraphPinLibrary
bp = unreal.load_asset('/Game/EscapeRoom/Blueprints/BP_RoomGenerator')
base = '/Game/EscapeRoom/Blueprints/BP_RoomGenerator.BP_RoomGenerator:GenerateRoom.'
n = lambda nm: unreal.find_object(None, base + nm)
CUSTOM = ['K2Node_AppendSpots', 'K2Node_AttachNoteA', 'K2Node_AttachNoteB', 'K2Node_BranchHard', 'K2Node_BranchNotes', 'K2Node_BranchSpots', 'K2Node_ButtonLabel', 'K2Node_CastLabel', 'K2Node_CodeStr', 'K2Node_CollideMedium', 'K2Node_DestroyOldNote', 'K2Node_DiffGet_A', 'K2Node_DiffGet_B', 'K2Node_DiffGet_C', 'K2Node_DiffGet_H', 'K2Node_DiffGet_S', 'K2Node_DiffPlusOne', 'K2Node_DiffWrap', 'K2Node_DummyFirst', 'K2Node_FindFurniture', 'K2Node_FindOldNotes', 'K2Node_FirstHalf', 'K2Node_ForEachFurniture', 'K2Node_ForEachOldNote', 'K2Node_FreeSlotsGetA', 'K2Node_FreeSlotsGetB', 'K2Node_GetDiffButton', 'K2Node_GetMediumSpots', 'K2Node_GetSelDiffA', 'K2Node_GetSelDiffB', 'K2Node_HardAppend', 'K2Node_HardAttach0', 'K2Node_HardAttach1', 'K2Node_HardAttach2', 'K2Node_HardAttach3', 'K2Node_HardCodeGet', 'K2Node_HardCodeStr', 'K2Node_HardCodeText', 'K2Node_HardDigit0', 'K2Node_HardDigit1', 'K2Node_HardDigit2', 'K2Node_HardDigit3', 'K2Node_HardLen0', 'K2Node_HardLen1', 'K2Node_HardLen2', 'K2Node_HardLen3', 'K2Node_HardMax0', 'K2Node_HardMax1', 'K2Node_HardMax2', 'K2Node_HardMax3', 'K2Node_HardNoteText0', 'K2Node_HardNoteText1', 'K2Node_HardNoteText2', 'K2Node_HardNoteText3', 'K2Node_HardPick0', 'K2Node_HardPick1', 'K2Node_HardPick2', 'K2Node_HardPick3', 'K2Node_HardPre0', 'K2Node_HardPre1', 'K2Node_HardPre2', 'K2Node_HardPre3', 'K2Node_HardRand0', 'K2Node_HardRand1', 'K2Node_HardRand2', 'K2Node_HardRand3', 'K2Node_HardRemove0', 'K2Node_HardRemove1', 'K2Node_HardRemove2', 'K2Node_HardRemove3', 'K2Node_HardSetSpot0', 'K2Node_HardSetSpot1', 'K2Node_HardSetSpot2', 'K2Node_HardSetSpot3', 'K2Node_HardSetText0', 'K2Node_HardSetText1', 'K2Node_HardSetText2', 'K2Node_HardSetText3', 'K2Node_HardSpawn0', 'K2Node_HardSpawn1', 'K2Node_HardSpawn2', 'K2Node_HardSpawn3', 'K2Node_HardSpotGetA0', 'K2Node_HardSpotGetA1', 'K2Node_HardSpotGetA2', 'K2Node_HardSpotGetA3', 'K2Node_HardSpotGetR0', 'K2Node_HardSpotGetR1', 'K2Node_HardSpotGetR2', 'K2Node_HardSpotGetR3', 'K2Node_HardSpotGetT0', 'K2Node_HardSpotGetT1', 'K2Node_HardSpotGetT2', 'K2Node_HardSpotGetT3', 'K2Node_HardSpotT0', 'K2Node_HardSpotT1', 'K2Node_HardSpotT2', 'K2Node_HardSpotT3', 'K2Node_HardSpots', 'K2Node_HardSpotsMedium', 'K2Node_HardStream0', 'K2Node_HardStream1', 'K2Node_HardStream2', 'K2Node_HardStream3', 'K2Node_HardSuf0', 'K2Node_HardSuf1', 'K2Node_HardSuf2', 'K2Node_HardSuf3', 'K2Node_HardText0', 'K2Node_HardText1', 'K2Node_HardText2', 'K2Node_HardText3', 'K2Node_HiddenIfNotPlaced', 'K2Node_HideMedium', 'K2Node_IsEasy', 'K2Node_IsEasyNow', 'K2Node_IsHard', 'K2Node_IsMediumA', 'K2Node_IsMediumB', 'K2Node_IsMediumC', 'K2Node_IsMediumNow', 'K2Node_IsMediumPiece', 'K2Node_IsMediumS', 'K2Node_LabelBranch', 'K2Node_LabelEasyStr', 'K2Node_LabelHardStr', 'K2Node_LabelMediumStr', 'K2Node_MoveFurniture', 'K2Node_NotMediumPiece', 'K2Node_NoteTextCompA', 'K2Node_NoteTextCompB', 'K2Node_PlaceBranch', 'K2Node_PosterIdxStr', 'K2Node_PosterRand', 'K2Node_PosterStream', 'K2Node_PosterTagName', 'K2Node_PosterTagStr', 'K2Node_RemoveUsedSpot', 'K2Node_SecondHalf', 'K2Node_SetChosenSlot', 'K2Node_SetGenDifficulty', 'K2Node_SetLabelEasy', 'K2Node_SetLabelHard', 'K2Node_SetLabelMedium', 'K2Node_SetNoteTextA', 'K2Node_SetNoteTextB', 'K2Node_SetSecondSpot', 'K2Node_SetSelDiff', 'K2Node_ShouldPlace', 'K2Node_SlotCount', 'K2Node_SlotMax', 'K2Node_SlotPick', 'K2Node_SlotRand', 'K2Node_SlotTransform', 'K2Node_SpawnNoteA', 'K2Node_SpawnNoteB', 'K2Node_SpotCount2', 'K2Node_SpotGetAA', 'K2Node_SpotGetAB', 'K2Node_SpotGetR', 'K2Node_SpotGetTA', 'K2Node_SpotGetTB', 'K2Node_SpotMax2', 'K2Node_SpotPick2', 'K2Node_SpotRand2', 'K2Node_SpotTransformA', 'K2Node_SpotTransformB', 'K2Node_StreamGet2', 'K2Node_StreamGetS', 'K2Node_Sym0', 'K2Node_Sym1', 'K2Node_Sym2', 'K2Node_Sym3', 'K2Node_SymAttachPoster', 'K2Node_SymMul', 'K2Node_SymOrder', 'K2Node_SymOrderText', 'K2Node_SymPaperComp', 'K2Node_SymPaperScale', 'K2Node_SymPermGet', 'K2Node_SymPosterGetA', 'K2Node_SymPosterGetT', 'K2Node_SymPosterPick', 'K2Node_SymPosterSpots', 'K2Node_SymPosterT', 'K2Node_SymPosterText', 'K2Node_SymPosterTextComp', 'K2Node_SymRand', 'K2Node_SymSetPerm', 'K2Node_SymSetSpot', 'K2Node_SymSpawnPoster', 'K2Node_SymStream', 'K2Node_Text1', 'K2Node_Text1Str', 'K2Node_Text2', 'K2Node_Text2Str', 'K2Node_UseSlot']
CLASSES = ['K2Node_CallFunction', 'K2Node_CallArrayFunction', 'K2Node_VariableGet', 'K2Node_VariableSet', 'K2Node_IfThenElse',
           'K2Node_MacroInstance', 'K2Node_SpawnActorFromClass', 'K2Node_GetArrayItem', 'K2Node_PromotableOperator',
           'K2Node_DynamicCast', 'K2Node_FunctionEntry', 'K2Node_FunctionResult', 'K2Node_Knot', 'K2Node_Select', 'K2Node_CommutativeAssociativeBinaryOperator']
nodes = {}
for nm in CUSTOM:
    x = n(nm)
    if x: nodes[nm] = x
for c in CLASSES:
    for i in range(0, 300):
        x = n('%s_%d' % (c, i))
        if x: nodes[x.get_name()] = x
EXEC_OUT = {'then', 'else', 'LoopBody', 'Completed', 'CastFailed'}
EXEC_IN = {'execute', 'Exec'}
def ins(x): return {str(PL.get_pin_name(p)): p for p in L.list_input_pins(x)}
def outs(x): return {str(PL.get_pin_name(p)): p for p in L.list_output_pins(x)}
def linked(p): return [PL.get_owning_node(q).get_name() for q in PL.list_connected_pins(p)]
entry = n('K2Node_FunctionEntry_0')
need, todo = {entry.get_name()}, [entry.get_name()]
nodes[entry.get_name()] = entry
while todo:                                   # follow the white exec wires from the entry
    nm = todo.pop(); x = nodes.get(nm) or n(nm)
    if not x: print('CLEAN missing', nm); continue
    nodes[nm] = x
    for k, p in outs(x).items():
        if k in EXEC_OUT:
            for m in linked(p):
                if m not in need: need.add(m); todo.append(m)
todo = list(need)
while todo:                                   # plus every node that feeds a value into those
    nm = todo.pop(); x = nodes.get(nm) or n(nm)
    if not x: print('CLEAN missing', nm); continue
    nodes[nm] = x
    for k, p in ins(x).items():
        if k in EXEC_IN: continue
        for m in linked(p):
            if m not in need: need.add(m); todo.append(m)
junk = sorted(set(nodes) - need)
print('CLEAN total', len(nodes), 'used', len(need), 'unused', len(junk))
for nm in junk:
    print('CLEAN junk', nm, str(L.get_node_title(nodes[nm])).replace('\n', ' '))
try:
    print('CLEAN pos', entry.get_editor_property('node_pos_x'), entry.get_editor_property('node_pos_y'))
except Exception as e:
    print('CLEAN pos err', e)
if DELETE:
    for nm in junk:
        for p in list(L.list_input_pins(nodes[nm])) + list(L.list_output_pins(nodes[nm])):
            PL.break_pin_links(p)
    print('CLEAN removed', L.remove_unused_nodes(bp))
    L.compile_blueprint(bp)
    print('CLEAN saved', unreal.EditorAssetLibrary.save_loaded_asset(bp))
