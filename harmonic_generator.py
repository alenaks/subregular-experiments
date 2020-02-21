from random import randint, choice

class Harmony(object):
    
    """
    Class defining the toy generator for the harmonic datasets.
    
    Attributes:
        cl_members (dict): dictionary of the type {(harmonic_class_1):class_id_1,
            (harmonic_class_2):class_id_2, ...} that contains info about the present
            harmonic classes. Note that the transparent element can be encoded by 
            a harmonic class containing a single element.
            Example: {("a", "o"):"A", ("b", "p"):"B", ("c"):"C"}
        cl_lengths (dict): dictionary of the type {class_id:(min_len, max_len)},
            where min_len and max_len denote the min and max len of the cluster
            made out of elements of class_id.
            Example: {"A":(1, 3), "B":(2, 4), "C":(4, 8)}
        blockers (dict): dictionary of the type {"b_1":"u_1", "b_2":"u_2", ...} where
            "b" is the blocker, and "u" is the newly introduced value.
            Example: {"t":"p"}
        blocker_prob (int): a chance of observing a blocker, the P evaluates from
            (1/blocker_prob).
            Example: 5
    """
    
    def __init__(self, cl_members, cl_lengths = None, blockers = None, blocker_prob = 5):
        """
        Init function for the Harmony class.
        """
        self.cl_members = cl_members
        if cl_lengths is not None:
            self.cl_lengths = cl_lengths
        else:
            self.cl_lengths = {i:(1, 3) for i in self.cl_members.values()}
        self.blockers = blockers
        self.blocker_prob = blocker_prob
        

        
    def generate_words(self, n = 3, length = 10):
        """
        Generates n strings of a given length.
        
        Arguments:
            n (int): how many strings need to be generated;
            length (int): length of the strings.
            
        Returns:
            list[str]: n generated strings.
        """
        # check if the harmony rules are well-formed
        if not self._verify_classes():
            raise("Cannot generate dataset: the sets are overlapping.")
            
        # unpack the dictionary for a quicker lookup
        unpacked = self._unpack_classes()
        transparent = self._transparent()
        generated = [self._generate(unpacked, length) for i in range(n)]
        return generated
    

    def generate_pairs(self, n = 3, length = 10):
        """
        Generates n pairs of strings of a given length.
        
        Arguments:
            n (int): how many strings need to be generated;
            length (int): length of the strings.
            
        Returns:
            list[tuple[str]]: n generated pairs of strings.
        """
        transparent = self._transparent()
        outputs = self.generate_words(n, length)
        inputs = self._mask_words(outputs, transparent)
        return list(zip(inputs, outputs))
        
        
    def _generate(self, unpacked, length):
        """
        Generates a set of strings; helper function.
        
        Output type: list[str]
        """
        
        # initialize the specifications of this particular string
        string = ""
        specs = self._specify()
        
        while len(string) < length:
            
            # check if we can now output the blocker
            if self.blockers is not None:
                if randint(1, self.blocker_prob) == 1:
                    b = choice(list(self.blockers))
                    string += b
                    
                    if len(string) == length:
                        return string
                    
                    # rewrite the specification because of the blocker
                    if self.blockers[b] not in specs:
                        for spec in specs:
                            if unpacked[spec] == unpacked[self.blockers[b]]:
                                specs.remove(spec)
                                specs.append(self.blockers[b])
                                break
                                
            # make sure that we don't generate cluster of the same
            # harminic set as the previous one
            if len(string) > 0:
                change = string[-1] in unpacked
            else:
                change = False
            
            # select and add new possible character as many times as
            # cl_lengths indicate
            if not change:
                newchar = choice(specs)
            else:
                collection = [i for i in specs]
                collection.remove(string[-1])
                newchar = choice(collection)
            freq_b, freq_e = self.cl_lengths[unpacked[newchar]]
            string += newchar * randint(freq_b, freq_e)
            
            # output
            if len(string) > length:
                string = ""
            elif len(string) == length:
                return string
            
            
    def _mask(self, string, transparent):
        """
        Masks all non-initial mentions of the specified allophone: helper function.
        
        Output type: str
        """
        classes = {i:False for i in self.cl_members.keys()}
        undergoers = self._undergoers()
        new = ""
        for s in string:
            if (s in undergoers) and (s not in transparent.values()):
                for c in classes:
                    
                    # rewrite the non-initial mention of the harmonic set member
                    # as its harmony_class_id
                    if s in c and not classes[c]:
                        classes[c] = True
                        new += s
                    elif s in c:
                        new += self.cl_members[c]
            else:
                new += s
        return new

    
    def _mask_words(self, words, transparent):
        """
        Masks every word of a given list; helper function.
        
        Output type: list[str]
        """
        return [self._mask(w, transparent) for w in words]
            
            
    def _undergoers(self):
        """
        Collects all undergoers; helper function.
        
        Output type: list[char]
        """
        items = []
        for i in self.cl_members:
            items.extend(list(i))
        return items
    
    def _transparent(self):
        """
        Checks if there are transparent items, i.e. if there is
        a harmonic class or classes that only contain a single item.
        
        Output type: dict[str:str]
        """
        transparent = dict()
        for i in self.cl_members:
            if len(i) == 1:
                transparent[self.cl_members[i]] = i[0]
        return transparent
        
        
    def _verify_classes(self):
        """
        Verifies that no set (harmonic sets or the set of blockers)
        overlaps with each other.
        
        Output type: bool
        """
        items = self._undergoers()
        if self.blockers is not None:
            block_ok = all([i not in items for i in self.blockers])
        else:
            block_ok = True
        return len(items) == len(set(items)) and block_ok
    
    
    def _unpack_classes(self):
        """
        Creates a dictionary where every harmonizing element 
        is mapped to its harmonic class; helps to optimize 
        the lookup of this information.
        
        Output type: dict
        """
        items = self._undergoers()
        unpacked = {}
        for i in items:
            for j in self.cl_members:
                if i in j:
                    unpacked[i] = self.cl_members[j]
        return unpacked

    
    def _specify(self):
        """
        Randomly initialize a specification from all given
        harmonic datasets.
        
        Output type: list[char]
        """
        return list(map(choice, self.cl_members.keys()))
