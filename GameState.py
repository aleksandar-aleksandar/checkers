import json
class GameState:
    
    def __init__(self,red_pawns, black_pawns, red_kings, black_kings, current_turn ):
        self.red_pawns = red_pawns
        self.black_pawns = black_pawns
        self.red_kings = red_kings
        self.black_kings = black_kings
        self.current_turn = current_turn
        self.eval_cache = {}

    def rewrite_matrix(self, game_state):
        matrix =  [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]

        for i in range(8):
            for j in range(8):
                matrix[i][j] = 0
        for i in range(len(game_state.red_pawns)):
            matrix[game_state.red_pawns[i][0]][game_state.red_pawns[i][1]] = 1
        for i in range(len(game_state.black_pawns)):
            matrix[game_state.black_pawns[i][0]][game_state.black_pawns[i][1]] = -1
        for i in range(len(game_state.red_kings)):
            matrix[game_state.red_kings[i][0]][game_state.red_kings[i][1]] = 2
        for i in range(len(game_state.black_kings)):
            matrix[game_state.black_kings[i][0]][game_state.black_kings[i][1]] = -2
            
        return matrix

    def rewrite_matrix_to_string(self, matrix):
        string = ""
        for i in range(8):
            for j in range(8):
                string += str(matrix[i][j])
        return string
    
    def rewrite_board(self,matrix):
        red_pawns = []
        black_pawns = []
        red_kings = []
        black_kings = []
        for i in range(8):
            for j in range(8):
                if matrix[i][j] == 1:
                    red_pawns.append((i,j))
                elif matrix[i][j] == -1:
                    black_pawns.append((i,j))
                elif matrix[i][j] == 2:
                    red_kings.append((i,j))
                elif matrix[i][j] == -2:
                    black_kings.append((i,j))
        return GameState(red_pawns, black_pawns, red_kings, black_kings, self.current_turn)
    
    def is_valid_move(self, start_pos, end_pos, color, is_king):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if not (0 <= end_row < 8 and 0 <= end_col < 8):
            return False

        if (end_row, end_col) in self.red_pawns or (end_row, end_col) in self.black_pawns or (end_row, end_col) in self.red_kings or (end_row, end_col) in self.black_kings:
            return False

        direction = 1 if color == "red" else -1

        if is_king:
            directions = [1, -1]
        else:
            directions = [direction]

        for direction in directions:
            if end_row == start_row + direction and abs(end_col - start_col) == 1:
                return True
            if end_row == start_row + 2 * direction and abs(end_col - start_col) == 2:
                mid_row = (start_row + end_row) // 2
                mid_col = (start_col + end_col) // 2
                if color == "red" and ((mid_row, mid_col) in self.black_pawns or (mid_row, mid_col) in self.black_kings):
                    return True
                elif color == "black" and ((mid_row, mid_col) in self.red_pawns or (mid_row, mid_col) in self.red_kings):
                    return True

        return False

    def calculate_valid_moves(self, pawn_pos, color, is_king):
        moves = []
        directions = [1, -1] if is_king else [1] if color == "red" else [-1]
        for direction in directions:
            for dc in [-1, 1]:
                new_row = pawn_pos[0] + direction
                new_col = pawn_pos[1] + dc
                if self.is_valid_move(pawn_pos, (new_row, new_col), color, is_king):
                    moves.append((new_row, new_col))

                new_row = pawn_pos[0] + 2 * direction
                new_col = pawn_pos[1] + 2 * dc
                if self.is_valid_move(pawn_pos, (new_row, new_col), color, is_king):
                    moves.append((new_row, new_col))

        return moves

    def get_possible_moves(self, game_state):
        possible_moves = []
        if(game_state.current_turn == "black"):
            for pawn in game_state.black_pawns:
                if(len(game_state.calculate_valid_moves(pawn, game_state.current_turn, False)) != 0):
                    for move in game_state.calculate_valid_moves(pawn, game_state.current_turn,False):
                        possible_moves.append((pawn,move))

            for king in game_state.black_kings:
                if(len(game_state.calculate_valid_moves(king, game_state.current_turn, True)) != 0):
                    for move in game_state.calculate_valid_moves(king, game_state.current_turn, True):
                        possible_moves.append((king,move))
                        
        else:
            for pawn in game_state.red_pawns:
                if(len(game_state.calculate_valid_moves(pawn, game_state.current_turn, False)) != 0):
                    for move in game_state.calculate_valid_moves(pawn, game_state.current_turn,False):
                        possible_moves.append((pawn,move))
            for king in game_state.red_kings:
                if(len(game_state.calculate_valid_moves(king, game_state.current_turn, True)) != 0):
                    for move in game_state.calculate_valid_moves(king, game_state.current_turn, True):
                        possible_moves.append((king,move))

        return possible_moves

    def get_possible_states(self, game_state, depth):
        if depth == 0:
            return []

        possible_states = []
        for move in self.get_possible_moves(game_state):
            new_state = self.apply_move(move, game_state)
            sub_states = self.get_possible_states(new_state, depth - 1) 
            possible_states.append((depth,new_state))
            possible_states.extend(sub_states)

        return possible_states
    
    def get_possible_evals(self,all_states):
        evals = []
        for state in all_states:
            evals.append((state[0], state[1].evaluate(state[1])))
        return evals

    def apply_move(self, move, game_state):
        state = self.rewrite_matrix(game_state)
        if(move):
            start_pos, end_pos = move
            start_row, start_col = start_pos
            end_row, end_col = end_pos
            if abs(start_row - end_row)>=2 and abs(start_col - end_col) >=2:
                mid_row = (start_row + end_row) // 2
                mid_col = (start_col + end_col) // 2
                state[mid_row][mid_col] = 0
            if(game_state.current_turn == "black" and end_row == 0):
                state[end_row][end_col] = -2
                state[start_row][start_col] = 0
            elif(game_state.current_turn == "red" and end_row == 7):
                state[end_row][end_col] = 2
                state[start_row][start_col] = 0
            else:
                state[end_row][end_col] = state[start_row][start_col]
                state[start_row][start_col] = 0

            gameState = self.rewrite_board(state)

            return gameState

    def is_terminal(self, game_state):
        if not game_state.red_pawns and not game_state.red_kings:
            return True 
        if not game_state.black_pawns and not game_state.black_kings:
            return True  
        
        if game_state.current_turn == "red":
            if not any(game_state.calculate_valid_moves(pawn, "red", False) for pawn in game_state.red_pawns) and not any(game_state.calculate_valid_moves(king, "red", True) for king in game_state.red_kings):
                return True 
        else:
            if not any(game_state.calculate_valid_moves(pawn, "black", False) for pawn in game_state.black_pawns) and not any(game_state.calculate_valid_moves(king, "black", True) for king in game_state.black_kings):
                return True  

        return False

    def evaluate(self, game_state):
        eval_score = 0

        for piece_type, pieces, color_value in [("pawn", game_state.red_pawns, -3), ("pawn", game_state.black_pawns, 3),
                                                ("king", game_state.red_kings, -10), ("king", game_state.black_kings, 10)]:
            for piece in pieces:
                row, col = piece
                if piece_type == "pawn":
                   
                    eval_score += color_value
                  
                    eval_score += color_value * (1 + col * 0.2) 
                    
                    eval_score += color_value * (3 if col in [0, 7] else 0)

                    eval_score += color_value * (2 if 2 <= row <= 5 and 2 <= col <= 5 else 0)

                    if any((row + dr, col + dc) in pieces for dr in [-1, 1] for dc in [-1, 1]):
                        eval_score += color_value * 0.2  

                    if color_value == -1 and row in [6, 7]:
                        eval_score += color_value * 1  
                    elif color_value == 1 and row in [0, 1]:
                        eval_score += color_value * 1  
                elif piece_type == "king":
             
                    eval_score += color_value
              
                    eval_score -= color_value * (2.6 if col in [0, 7] else 0)  
                
                    if any((row + dr, col + dc) in pieces for dr in [-1, 1] for dc in [-1, 1]):
                        eval_score += color_value * 0.2  

        red_mobility = sum(len(game_state.calculate_valid_moves(piece, "red", False)) for piece in game_state.red_pawns) + sum(len(game_state.calculate_valid_moves(piece, "red", True)) for piece in game_state.red_kings)
        black_mobility = sum(len(game_state.calculate_valid_moves(piece, "black", False)) for piece in game_state.black_pawns) + sum(len(game_state.calculate_valid_moves(piece, "black", True)) for piece in game_state.black_kings)
        eval_score += (black_mobility - red_mobility) * 0.1  
        

        return eval_score

    def save_cache_to_json(self, filename, cache):
        with open(filename, 'w') as file:
            json.dump(cache, file)

    def load_cache_from_json(filename):
        try:
            with open(filename, 'r') as file:
                cache_data = json.load(file)
                return cache_data
        except FileNotFoundError:
            print(f"Warning: File '{filename}' not found. Creating an empty cache.")
            return {}
        except json.decoder.JSONDecodeError:
            print(f"Warning: File '{filename}' contains invalid JSON data. Creating an empty cache.")
            return {}

    def minimax(self, game_state, depth, alpha, beta, maximizing_player, cache):
        if depth == 0 or game_state.is_terminal(game_state):
            eval_result = game_state.evaluate(game_state)
            return eval_result, None

        self.eval_cache = cache
        best_move = None
        state_key = self.rewrite_matrix_to_string(game_state.rewrite_matrix(game_state))
        if state_key in self.eval_cache:
            return self.eval_cache[state_key]

        if maximizing_player:
            max_eval = float('-inf')
            for move in game_state.get_possible_moves(game_state):
                new_state = game_state.apply_move(move, game_state)
                eval, _ = new_state.minimax(new_state, depth - 1, alpha, beta, False, cache)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in game_state.get_possible_moves(game_state):
                new_state = game_state.apply_move(move, game_state)
                eval, _ = new_state.minimax(new_state, depth - 1, alpha, beta, True, cache)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return min_eval, best_move

    def write_the_best_move_in_cache(self,game_state, depth, alpha, beta, maximizing_player, cache):
        the_best_move = self.minimax(game_state, depth, alpha, beta, maximizing_player, cache)
        key = self.rewrite_matrix_to_string(game_state.rewrite_matrix(game_state))
        self.eval_cache[key] = the_best_move
        self.save_cache_to_json("eval_cache.json", self.eval_cache)

