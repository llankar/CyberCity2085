extends RefCounted
## QA decisions only; invokes production input handlers and never sets combat state.
var policy := "objective"
var moves := 0
var attacks := 0
var interactions := 0
var _turn := -1
var _blocked := {}

func act(scene) -> bool:
	if _turn!=scene.turn_number:
		_turn=scene.turn_number;_blocked.clear()
	var active: int = scene.active_player_index
	if active < 0 or active >= scene.player_units.size(): return false
	var unit: Dictionary = scene.player_units[active]
	if int(unit.get("hp", 0)) <= 0 or int(unit.get("ap", 0)) <= 0 or _blocked.has(active):
		for i in range(scene.player_units.size()):
			if int(scene.player_units[i].hp)>0 and int(scene.player_units[i].ap)>0 and not _blocked.has(i):
				scene._on_unit_clicked(i,false)
				return true
		return false
	var origin: Vector2i = scene._cell_position(unit)
	if policy == "objective" and scene.objective.get("needs_marker", false):
		var target: Vector2i = scene.objective.cell
		if distance(origin,target) <= int(scene.objective.get("interact_range", 2)):
			scene._on_cell_clicked(target)
			interactions += 1
			return true
	if policy != "passive":
		var best := ""
		var enemy_index := -1
		var score := -1.0
		for action in unit.get("available_actions", []):
			if scene._action_type(action) not in ["FIRE", "MELEE"]: continue
			var cost: int = scene._action_ap_cost(action)
			if cost > int(unit.ap): continue
			for i in range(scene.enemy_units.size()):
				var enemy: Dictionary = scene.enemy_units[i]
				if int(enemy.hp) <= 0: continue
				var cell: Vector2i = scene._cell_position(enemy)
				if distance(origin,cell) > scene._action_range(action) or not scene._battlefield.has_los(origin,cell,[]): continue
				var value := float(scene._action_damage(action))/float(maxi(1,cost))
				if value > score: score=value; best=action; enemy_index=i
		if enemy_index >= 0:
			var before_ap: int=int(unit.ap)
			scene._on_action_pressed(best)
			scene._on_unit_clicked(enemy_index,true)
			if int(scene.player_units[active].ap)<before_ap or scene.battle_ended:
				attacks += 1
				return true
			_blocked[active]=true
			return false
	# Find a legal, unoccupied destination along the shortest reachable route.
	var targets: Array[Vector2i] = []
	if policy == "objective" and scene.objective.get("needs_marker", false): targets.append(scene.objective.cell)
	for enemy: Dictionary in scene.enemy_units:
		if int(enemy.hp)>0: targets.append(scene._cell_position(enemy))
	var best_cell := origin
	var best_remaining := 100000
	for destination: Vector2i in scene._battlefield.reachable_cells(origin,int(unit.ap)):
		if destination==origin or scene._is_cell_occupied(destination,active,-1):continue
		for target: Vector2i in targets:
			var path: Array[Vector2i]=scene._battlefield.find_path(destination,target)
			if path.is_empty():continue
			var remaining:=path.size()
			if remaining<best_remaining:best_remaining=remaining;best_cell=destination
	if best_cell!=origin:
		scene._on_action_pressed("Move")
		scene._on_cell_clicked(best_cell)
		if scene._cell_position(scene.player_units[active])!=origin:
			moves += 1
			return true
	if policy == "passive": return false
	_blocked[active]=true
	# Let the next available agent act through the same portrait-selection handler.
	for offset in range(1,scene.player_units.size()):
		var index: int = (active+offset)%scene.player_units.size()
		if int(scene.player_units[index].hp)>0 and int(scene.player_units[index].ap)>0 and not _blocked.has(index):
			scene._on_unit_clicked(index,false)
			return true
	return false

func distance(a: Vector2i,b: Vector2i) -> int: return absi(a.x-b.x)+absi(a.y-b.y)
