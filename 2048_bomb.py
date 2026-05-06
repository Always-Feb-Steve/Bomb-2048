import sys
import random
import itertools


def slide(seqs, direction=0):
    non_zero=[n for n in seqs if n!=0]
    if direction==0:
        temp=non_zero+[0,0,0,0]
        result=temp[:4]
    else:
        temp=[0,0,0,0]+non_zero
        result=temp[-4:]
    return result

def sum_seqs(seqs, direction=0):
    if direction==0:
        if seqs[0] and seqs[1] and seqs[0]==seqs[1]:
            seqs[0]=seqs[0]*2
            seqs[1]=0

            if seqs[2] and seqs[3] and seqs[2]==seqs[3]:
                seqs[2]=seqs[2]*2
                seqs[3]=0

        else:
            if seqs[1] and seqs[2] and seqs[1]==seqs[2]:
                seqs[1]=seqs[1]*2
                seqs[2]=0

            if seqs[2] and seqs[3] and seqs[2]==seqs[3]:
                seqs[2]=seqs[2]*2
                seqs[3]=0

    else:
        if seqs[2] and seqs[3] and seqs[2]==seqs[3]:
            seqs[3]=seqs[3]*2
            seqs[2]=0

            if seqs[0] and seqs[1] and seqs[0]==seqs[1]:
                seqs[1]=seqs[1]*2
                seqs[0]=0

        else:
            if seqs[1] and seqs[2] and seqs[1]==seqs[2]:
                seqs[2]=seqs[2]*2
                seqs[1]=0

            if seqs[0] and seqs[1] and seqs[1]==seqs[0]:
                seqs[1]=seqs[1]*2
                seqs[0]=0

    return slide(seqs, direction=direction)


def calc_bomb_increment(seqs, direction, bomb_pos):
    result = sum_seqs(slide(seqs[:], direction=direction), direction=direction)
    if direction == 0:
        before = sum(v for i, v in enumerate(seqs) if i > bomb_pos)
        after = sum(v for i, v in enumerate(result) if i > bomb_pos)
    else:
        before = sum(v for i, v in enumerate(seqs) if i < bomb_pos)
        after = sum(v for i, v in enumerate(result) if i < bomb_pos)
    return before - after


def up(grid, bomb_pos=None):
    increment = 0
    for col in range (4):
        column=[]
        for row in range (4):
            column.append(grid[row][col])

        if bomb_pos and col == bomb_pos[1]:
            increment += calc_bomb_increment(column, 0, bomb_pos[0])

        column=slide(column, direction=0)
        column=sum_seqs(column, direction=0)

        for row in range (4):
            grid[row][col]=column[row]

    return grid, increment

def down(grid, bomb_pos=None):
    increment = 0
    for col in range (4):
        column=[]
        for row in range (4):
            column.append(grid[row][col])

        if bomb_pos and col == bomb_pos[1]:
            increment += calc_bomb_increment(column, 1, bomb_pos[0])

        column=slide(column, direction=1)
        column=sum_seqs(column, direction=1)

        for row in range (4):
            grid[row][col]=column[row]

    return grid, increment

def left(grid, bomb_pos=None):
    result=[]
    increment = 0
    for r, row in enumerate(grid):
        if bomb_pos and r == bomb_pos[0]:
            increment += calc_bomb_increment(row, 0, bomb_pos[1])
        row_after_slide=slide(row, direction=0)
        row_after_sums=sum_seqs(row_after_slide, direction=0)
        result.append(row_after_sums)
    return result, increment

def right(grid, bomb_pos=None):
    result=[]
    increment = 0
    for r, row in enumerate(grid):
        if bomb_pos and r == bomb_pos[0]:
            increment += calc_bomb_increment(row, 1, bomb_pos[1])
        row_after_slide=slide(row, direction=1)
        row_after_sums=sum_seqs(row_after_slide, direction=1)
        result.append(row_after_sums)
    return result, increment




class Game:
    controls=["w", "a", "s", "d"] # wasd represents up, left, down, right
    BOMB_THRESHOLD = 200

    def choose_bomb_pos(self):
        return (random.randint(0, 3), random.randint(0, 3))

    def explode(self):
        br, bc = self.bomb_pos
        print(f'\n💥 BOOM! Explosion! Numbers around are halved!')
        for r in range(br - 1, br + 2):
            for c in range(bc - 1, bc + 2):
                if (r, c) != (br, bc) and 0 <= r < 4 and 0 <= c < 4:
                    val = self.grid[r][c] // 2
                    self.grid[r][c] = val if val >= 2 else 0
        self.bomb_count = 0
        self.bomb_pos = self.choose_bomb_pos()
        print(f'New Bomb is buried at [{self.bomb_pos[0]+1}, {self.bomb_pos[1]+1}]! \n')

    def rdm_field(self):
        number=random.choice([4,2])
        x,y=random.choice ([(x,y) for x, y in itertools.product([0,1,2,3],[0,1,2,3]) if self.grid[x][y]==0])
        self.grid[x][y]=number

    def print_screen(self):
        br, bc = self.bomb_pos
        RED = '\033[31m'
        RESET = '\033[0m'
        print('-' * 21)
        for r, row in enumerate(self.grid):
            cells = [str(col or ' ').center(4) for col in row]
            if r == br:
                row_str = ''
                for i in range(5):
                    bar = f'{RED}|{RESET}' if i == bc or i == bc + 1 else '|'
                    row_str += bar
                    if i < 4:
                        row_str += cells[i]
            else:
                row_str = '|{}|'.format('|'.join(cells))
            print(row_str)
            print('-' * 21)
        print(f'Bomb at [{br+1},{bc+1}] | Score: {self.bomb_count}/{self.BOMB_THRESHOLD} | Last Step: +{self.last_bomb_increment}')

    def logic(self, control):
        op_dict={'w': up, 'a': left, 's': down, 'd': right}
        user_op_func=op_dict[control]
        grid_copy=[]
        for row in self.grid:
            new_row=[]
            for col in row:
                new_row.append(col)
            grid_copy.append(new_row)
        grid, increment=user_op_func(grid_copy, self.bomb_pos)
        self.last_bomb_increment = increment

        if grid !=self.grid:
            del self.grid[:]
            self.grid.extend(grid)

            self.bomb_count += increment
            if self.bomb_count >= self.BOMB_THRESHOLD:
                self.explode()

            # GPT
            if [n for n in itertools.chain(*self.grid) if n >=2048]:
                return 1, 'You Win!'

            else:
                self.rdm_field()

        else:
            all_move_functions=[up,down,left,right]
            all_move_results=[]
            for move_func in all_move_functions:
                result, _=move_func([row[:] for row in self.grid], self.bomb_pos)
                all_move_results.append(result)

            valid = []
            for result_grid in all_move_results:
                if result_grid != self.grid:
                    valid.append(1)
            if not valid:
                return -1, 'You Lose!'


        return 0, ''


    def main_loop(self):
        self.grid=[[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
        self.bomb_pos = self.choose_bomb_pos()
        self.bomb_count = 0
        self.last_bomb_increment = 0
        self.rdm_field()
        self.rdm_field()
        print(f'The Bomb is buried at [{self.bomb_pos[0]+1}, {self.bomb_pos[1]+1}]. Watch Out! ')
        while True:
            self.print_screen()

            control=input('input w/a/s/d/')
            if control in self.controls:
                status, info=self.logic(control)
                if status: # status =1 or -1, meaning the user needs to start a new game
                    print (info)
                    print ("Start a new game? [Y/N]")
                    user_input=input()
                    if user_input=="Y":
                        break
                    else:
                        sys.exit(0)
        self.main_loop()



if __name__=='__main__':
    Game().main_loop()
