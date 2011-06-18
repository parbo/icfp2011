import unittest

import state
import command

class TestCommand(unittest.TestCase):
    def setUp(self):
        # Players:
        self.p0 = state.State()
        self.p1 = state.State()
        self.p0.opponent = self.p1
        self.p1.opponent = self.p0
        self.cmd = command.Command(self.p0)
        
    def play_moves(self, moves):
        for move in moves:
            self.p0.application(*move)
        
    def test_set_integer(self):
        moves = self.cmd.set_integer(10, 237)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[10]), '{10000,237}')
        
    def test_copy_slot(self):
        moves = self.cmd.set_integer(10, 237)
        moves.extend(self.cmd.copy_slot(10, 20))
        self.play_moves(moves)
        self.assertEqual(str(self.p0[10]), '{10000,237}')
        self.assertEqual(str(self.p0[20]), '{10000,237}')
        
    def test_append_int_param(self):
        self.p0.right_appl('help', 0)
        moves = self.cmd.append_int_param(0, 13)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[0]), '{10000,help(13)}')
        moves = self.cmd.append_int_param(0, 7)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[0]), '{10000,help(13)(7)}')
        
    def test_help_slot(self):
        moves = self.cmd.set_integer(10, 500)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[10]), '{10000,500}')
        moves = self.cmd.help_slot(4, 5, 0, 10)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p0[4]), '{9500,I}')
        self.assertEqual(str(self.p0[5]), '{10550,I}')
        self.assertEqual(str(self.p0[10]), '{10000,500}')
        
    def test_attack_slot(self):
        moves = self.cmd.set_integer(10, 500)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[10]), '{10000,500}')
        moves = self.cmd.attack_slot(4, 5, 0, 10)
        self.play_moves(moves)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p0[4]), '{9500,I}')
        self.assertEqual(str(self.p0[10]), '{10000,500}')
        self.assertEqual(str(self.p1[250]), '{9550,I}')
        
if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCommand)
    unittest.TextTestRunner(verbosity=2).run(suite)