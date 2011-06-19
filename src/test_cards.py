import unittest

import common
import state
import cards

class TestCards(unittest.TestCase):
    def setUp(self):
        # Players:
        self.p0 = state.State()
        self.p1 = state.State()
        self.p0.opponent = self.p1
        self.p1.opponent = self.p0

    def test_card_I(self):
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,zero}')
        
    def test_card_zero(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,1}')
        
    def test_card_succ(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.left_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,2}')
        for i in range(65532):
            self.p0.left_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,65534}')
        self.p0.left_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,65535}')
        self.p0.left_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,65535}')
        
    def test_card_dbl(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        for i in range(1, 16):
            self.p0.left_appl('dbl', 0)
            self.assertEqual(str(self.p0[0]), '{10000,%d}' % (2 ** i))
        self.p0.left_appl('dbl', 0)
        self.assertEqual(str(self.p0[0]), '{10000,65535}')
        
    def test_card_get(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.right_appl('zombie', 1)
        self.p0.left_appl('get', 0)
        self.assertEqual(str(self.p0[0]), '{10000,zombie}')
        
    def test_card_put(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('put', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        
    def test_card_S(self):
        self.p0.right_appl('succ', 0)
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(succ))}')
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(succ))(succ)}')
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,2}')
        
    def test_card_K(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('K', 0)
        self.assertEqual(str(self.p0[0]), '{10000,K(zero)}')
        self.p0.right_appl('I', 0)
        self.assertEqual(str(self.p0[0]), '{10000,zero}')
        
    def test_card_inc(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.left_appl('inc', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p0[1]), '{10001,I}')
        
    def test_card_inc_zombie(self):
        # 'inc' card in zombie mode.
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.zombie_appl = True
        self.p0.left_appl('inc', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p0[1]), '{9999,I}')
        
    def test_card_dec(self):
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.left_appl('dec', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p1[254]), '{9999,I}')
        
    def test_card_dec_zombie(self):
        # 'dec' card in zombie mode.
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.zombie_appl = True
        self.p0.left_appl('dec', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p1[254]), '{10001,I}')
        
    def test_card_attack(self):
        # attack(i=0, j=0, n=16)
        self.p0.right_appl('attack', 0)
        # Add parameters 'i' and 'j'.
        self.p0.right_appl('zero', 0)
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,attack(zero)(zero)}')
        # Fetch parameter 'n' with 'get[1]'.
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('get', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(attack(zero)(zero)))(get)}')
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(S(K(attack(zero)(zero)))(get)))(succ)}')
        # Set slot[1] = 16.
        self.p0.right_appl('zero', 1)
        self.p0.left_appl('succ', 1)
        for i in range(4):
            self.p0.left_appl('dbl', 1)
        self.assertEqual(str(self.p0[1]), '{10000,16}')
        # Perform attack.
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{9984,I}')
        self.assertEqual(str(self.p1[255]), '{9986,I}')
        
    def test_card_attack_zombie(self):
        # attack(i=0, j=0, n=16) in zombie mode.
        self.p0.right_appl('attack', 0)
        # Add parameters 'i' and 'j'.
        self.p0.right_appl('zero', 0)
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,attack(zero)(zero)}')
        # Fetch parameter 'n' with 'get[1]'.
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('get', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(attack(zero)(zero)))(get)}')
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(S(K(attack(zero)(zero)))(get)))(succ)}')
        # Set slot[1] = 16.
        self.p0.right_appl('zero', 1)
        self.p0.left_appl('succ', 1)
        for i in range(4):
            self.p0.left_appl('dbl', 1)
        self.assertEqual(str(self.p0[1]), '{10000,16}')
        # Perform attack.
        self.p0.zombie_appl = True
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{9984,I}')
        self.assertEqual(str(self.p1[255]), '{10014,I}')
        
    def test_card_help(self):
        # help(i=0, j=1, n=16)
        self.p0.right_appl('help', 0)
        # Add parameters 'i' and 'j'.
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(help(zero)))(succ)}')
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,help(zero)(1)}')
        # Fetch parameter 'n' with 'get[1]'.
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('get', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(help(zero)(1)))(get)}')
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(S(K(help(zero)(1)))(get)))(succ)}')
        # Set slot[1] = 16.
        self.p0.right_appl('zero', 1)
        self.p0.left_appl('succ', 1)
        for i in range(4):
            self.p0.left_appl('dbl', 1)
        self.assertEqual(str(self.p0[1]), '{10000,16}')
        # Do help call.
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{9984,I}')
        self.assertEqual(str(self.p0[1]), '{10017,16}')
        
    def test_card_help_zombie(self):
        # help(i=0, j=1, n=16) in zombie mode.
        self.p0.right_appl('help', 0)
        # Add parameters 'i' and 'j'.
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(help(zero)))(succ)}')
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,help(zero)(1)}')
        # Fetch parameter 'n' with 'get[1]'.
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('get', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(help(zero)(1)))(get)}')
        self.p0.left_appl('K', 0)
        self.p0.left_appl('S', 0)
        self.p0.right_appl('succ', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(K(S(K(help(zero)(1)))(get)))(succ)}')
        # Set slot[1] = 16.
        self.p0.right_appl('zero', 1)
        self.p0.left_appl('succ', 1)
        for i in range(4):
            self.p0.left_appl('dbl', 1)
        self.assertEqual(str(self.p0[1]), '{10000,16}')
        # Do help call.
        self.p0.zombie_appl = True
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{9984,I}')
        self.assertEqual(str(self.p0[1]), '{9983,16}')
        
    def test_card_copy(self):
        self.p1.right_appl('zero', 1)
        self.p0.right_appl('zero', 0)
        self.p0.left_appl('succ', 0)
        self.p0.left_appl('copy', 0)
        self.assertEqual(str(self.p0[0]), '{10000,zero}')
        
    def test_card_revive(self):
        self.p0.slots[0].vitality = 0
        self.p0.right_appl('zero', 2)
        self.p0.right_appl('zero', 3)
        self.p0.left_appl('succ', 3)
        self.p0.left_appl('revive', 2)
        self.p0.left_appl('revive', 3)
        self.assertEqual(str(self.p0[0]), '{1,I}')
        self.assertEqual(str(self.p0[1]), '{10000,I}')
        self.assertEqual(str(self.p0[2]), '{10000,I}')
        self.assertEqual(str(self.p0[3]), '{10000,I}')
        
    def test_card_zombie(self):
        self.p1.slots[255].vitality = 0
        self.p0.right_appl('zombie', 0)
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,zombie(zero)}')
        self.p0.right_appl('zero', 0)
        self.assertEqual(str(self.p0[0]), '{10000,I}')
        self.assertEqual(str(self.p1[255]), '{-1,zero}')
        
    def test_call_depth(self):
        self.p0.right_appl('S', 0)
        self.p0.right_appl('get', 0)
        self.p0.right_appl('I', 0)
        self.assertEqual(str(self.p0[0]), '{10000,S(get)(I)}')
        self.p0.right_appl('zero', 0)
        self.assertTrue(isinstance(self.p0.result, common.CallDepthExceeded))
        
    def test_apply_zombie(self):
        self.p0.right_appl('zero', 0)
        self.p0[0].vitality = -1
        self.p0.apply_zombies()
        self.assertEqual(str(self.p0[0]), '{0,I}')

if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCards)
    unittest.TextTestRunner(verbosity=2).run(suite)
