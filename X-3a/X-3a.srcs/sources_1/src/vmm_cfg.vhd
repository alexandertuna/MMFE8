--
-- VMM registers and configuration
-- this block handles the 1616 bit serial configuration
-- streams
--

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use IEEE.std_logic_unsigned.all;

Library UNISIM;
use UNISIM.vcomponents.all;

use work.vmm_pkg.all;

entity vmm_cfg is
    port
    (
        clk_ila				    : in 	STD_LOGIC;
        clk200				    : in 	STD_LOGIC;
        vmm_clk_200             : in 	STD_LOGIC; 
    	
	    clk100                  : in    STD_LOGIC;
        vmm_clk_100             : in 	STD_LOGIC; 
    	
    reset                       : in 	STD_LOGIC;

    cfg_bit_in                  : in	std_logic ;
    cfg_bit_out                 : out	std_logic ;
  
    vmm_ena_vmm_cfg_sm          : out   std_logic;
    vmm_ena_cfg_sr              : out   std_logic;
    vmm_ena_cfg_rst             : out   std_logic;
    vmm_wen_cfg_sr              : out   std_logic;
    vmm_wen_cfg_rst             : out   std_logic;

    vmm_ckdt_en_vec             : out   std_logic_vector( 7 DOWNTO 0);
    vmm_ckdt                    : in    std_logic ;
  
    vmm_ckart_en                : out   std_logic ;
    vmm_ckart                   : in    std_logic ;

    vmm_cktk_daq_en_vec	        : out   std_logic_vector( 7 DOWNTO 0) ; --from daq 
    vmm_cktk_cfg_sr_en          : out   std_logic ; --from config module

    vmm_cktk                    : in    std_logic ; 
  
    vmm_cktp_en                 : out   std_logic ;
    vmm_cktp                    : in    std_logic ; 
  
    vmm_ckbc_en                 : out std_logic ;
    vmm_ckbc                    : in std_logic ; 
    reset_bcid_counter          : out std_logic ; 

    vmm_data1_vec               : in  std_logic_vector( 7 DOWNTO 0);
    vmm_data0_vec               : in  std_logic_vector( 7 DOWNTO 0);
    vmm_art_vec                 : in  std_logic_vector( 7 DOWNTO 0);
    turn_counter                : in  std_logic_vector(15 downto 0); 

    wr_en                       : buffer   std_logic;

    vmm_rd_en                   : buffer   std_logic_vector( 7 DOWNTO 0);
    
    vmm_din_vec                 : out   array_8x32bit;    --from daq
    dt_cntr_intg0_vec           : out   array_Int_8;      --from daq
    dt_cntr_intg1_vec           : out   array_Int_8;      --from daq
    vmm_data_buf_vec            : out   array_8x38bit;    --from daq
    vmm_dout_vec                : out   array_8x32bit;    --from daq
    rr_state                    : buffer    std_logic_vector( 7 DOWNTO 0);
    din                         : buffer    std_logic_vector( 31 DOWNTO 0);

    vmm_ro                      : in   std_logic_vector(7 downto 0) ; 
    vmm_configuring             : out   std_logic ;
    rst_state                   : out   std_logic_vector( 2 downto 0);

    LEDx                        : out   std_logic_vector( 2 downto 0);
    testX                       : in    std_logic;

    axi_reg                     : in   array_80x32bit;  --axi config data

    vmm_cfg_sel                 : in STD_LOGIC_VECTOR(31 downto 0);

    -- AXI bus interface to the FIFO --
    axi_clk : in std_logic;

    --     signals from the round robin data fifo
    rr_data_fifo_rd_en          : in STD_LOGIC := '0';
    rr_data_fifo_dout           : out STD_LOGIC_VECTOR( 31 downto 0);    
    rr_data_fifo_empty          : out STD_LOGIC := '0';    
    rr_rd_data_count            : out STD_LOGIC_VECTOR( 9 downto 0);
    rr_wr_data_count            : out STD_LOGIC_VECTOR( 9 downto 0);
                        
    vmm_gbl_rst                 : in STD_LOGIC := '0';
    vmm_gbl_rst_sum             : out STD_LOGIC := '0'
);

end vmm_cfg;

architecture rtl of vmm_cfg is







-- components are here
COMPONENT fifo_round_robin
    PORT (
        rst             : IN STD_LOGIC;
        wr_clk          : IN STD_LOGIC;
        rd_clk          : IN STD_LOGIC;
        din             : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
        wr_en           : IN STD_LOGIC;
        rd_en           : IN STD_LOGIC;
        dout            : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
        full            : OUT STD_LOGIC;
        almost_full     : OUT STD_LOGIC;
        empty           : OUT STD_LOGIC;
        almost_empty    : OUT STD_LOGIC;
--        rd_data_count   : OUT STD_LOGIC_VECTOR( 10 DOWNTO 0);
--        wr_data_count   : OUT STD_LOGIC_VECTOR( 10 DOWNTO 0)
        rd_data_count   : OUT STD_LOGIC_VECTOR( 9 DOWNTO 0);
        wr_data_count   : OUT STD_LOGIC_VECTOR( 9 DOWNTO 0)
);
END COMPONENT; 


COMPONENT vmm_daq is
    port
    (
        vmm_clk_200               : in 	STD_LOGIC; 
	    reset					  : in 	STD_LOGIC;
        vmmNumber                 : in  std_logic_vector( 2 downto 0);

        vmm_data0                 : in  STD_LOGIC;
        vmm_data1                 : in  std_logic;
        vmm_art                   : in  std_logic;
        turn_counter              : in  std_logic_vector(15 downto 0); 
    
        vmm_cktk_daq_en	          : out   std_logic ;
        vmm_ckdt_en  	          : out   std_logic ;
    
        vmm_ckdt                  : in    std_logic ;
        vmm_ckart                 : in    std_logic ;
    
        din                       : out   std_logic_vector(31 downto 0);
        dt_cntr_intg0             : out   integer;
        dt_cntr_intg1             : out   integer;
        vmm_data_buf              : out   std_logic_vector(37 downto 0);
      
        rd_clk  	              : in    std_logic ;
        empty  	                  : out   std_logic ;
        rd_data_count   	      : out   std_logic_vector( 9 downto 0);
        wr_data_count             : out   std_logic_vector( 9 downto 0);
        rd_en                     : in    std_logic;
        dout                      : out   std_logic_vector(31 DOWNTO 0)
    );
	
END COMPONENT; 


---------------------=======================------------------
---------------------=====   Signals    ====------------------
---------------------=======================------------------


	signal probe0                          : STD_LOGIC_VECTOR(31 DOWNTO 0); 
    signal probe1                          : STD_LOGIC_VECTOR(31 DOWNTO 0);

    signal testX_i                         : std_logic := '0';
    signal vmm_data0_ii                    : std_logic := '0';
    signal vmm_data0_ii_ack                : std_logic := '0';
    signal dt_cntr                         : std_logic_vector( 4 downto 0);
    signal dt_cntr_p1                      : std_logic_vector( 4 downto 0);
    signal dt_cntr_p2                      : std_logic_vector( 4 downto 0);
    signal dt_cntr_p3                      : std_logic_vector( 4 downto 0);
    signal dt_cntr_p4                      : std_logic_vector( 4 downto 0);
    signal dt_state                        : std_logic_vector( 7 downto 0) := ( others => '0');

    signal dt_reset                        : std_logic ;
    signal dt_done                         : std_logic ;
        
    signal vmm_ckart_en_i                  : std_logic ;
    signal vmm_ckart_i                     : std_logic ;

    signal art_reset                       : std_logic;
    signal art_done                        : std_logic;
    signal art_data                        : std_logic_vector( 7 downto 0) := ( others => '0');
    signal art_state                       : std_logic_vector( 3 downto 0) := ( others => '0');

    signal clk_tk_sync_cnt                 : STD_LOGIC_VECTOR( 31 DOWNTO 0) :=x"00004047";

    signal vmm_empty                       : std_logic_vector( 7 downto 0) := ( others => '1');
    signal vmm_dout_vec_i                  : array_8x32bit;        
    signal axi_rdata_ls_vmm                : array_8x32bit;        
    signal axi_rdata_rcnt_vmm              : array_8x32bit;        
    signal vmm_rd_data_count               : array_8x10bit;        
    signal vmm_wr_data_count               : array_8x10bit;        

    signal axi_pop_vmm                     : std_logic_vector( 7 downto 0) := ( others => '1');

    signal cktp_i                          : std_logic;
    signal ckbc_i                          : std_logic;
    signal vmm_ckbc_en_i                   : std_logic ;
    signal vmm_cktp_en_i                   : std_logic ;
    signal vmm_clk_token_i                 : std_logic ;
    
	signal cfg_bit_in_i	                   : std_logic;
	signal cfg_bit_out_i                   : std_logic;		
	
    signal cfg_sm_cntr	                   : std_logic_vector(31 downto 0);
    signal cfg_rst_ctr	                   : std_logic_vector(31 downto 0);

	constant cfg_bits                      : integer := 1616 ; -- the useful bits
	constant cfg_bits_max                  : integer := 1632 ;
	
	signal regs_out                        : array_64x32bit;		
	signal regs_in                         : array_64x32bit;		

	signal statex                          : std_logic_vector(3 downto 0) ;
	signal bit_cntrx                       : std_logic_vector( 11 downto 0) ;
	
	signal vmm_run                         : std_logic;
    signal cfg_sr_done                     : std_logic ;
    signal vmm_rst_done                    : std_logic ; -- from VMM cfg SM
    signal gbl_rst                         : std_logic ;
    signal acq_rst                         : std_logic ;
    	
	-- make two shift registers 1616 bits long.
	-- one for writing to VMM and one for reading from VMM
	signal vmm_cfg_in                      : std_logic_vector(cfg_bits_max-1 downto 0) ;
	signal vmm_cfg_out                     : std_logic_vector(cfg_bits_max-1 downto 0) ;
	
	-- a larger number here will lengthen the time between token pulses
	signal token_cntr : std_logic_vector(4 downto 0) ; -- 32 ns pulse every 640 ns
		
    type state_t is (s0, s1, s2, s3, s4, s5, s6, s7, s8);
    signal state  : state_t;
	
	signal counter1                         : std_logic_vector (31 downto 0) := X"00000000";	
	signal ckbc_cntr                        : std_logic_vector (0 downto 0) := (others=>'0');
	signal delay_cntr                       : std_logic_vector (31 downto 0) := X"00000000";

    signal LEDxi                            : std_logic_vector( 2 downto 0);
    
    SIGNAL wr_clk_i                         : STD_LOGIC := '0';
    SIGNAL rd_clk_i                         : STD_LOGIC := '0';
    SIGNAL wr_data_count                    : STD_LOGIC_VECTOR( 10-1 DOWNTO 0) := (OTHERS => '0');
    SIGNAL rd_data_count                    : STD_LOGIC_VECTOR( 10-1 DOWNTO 0) := (OTHERS => '0');
    SIGNAL almost_full                      : STD_LOGIC := '0';
    SIGNAL almost_empty                     : STD_LOGIC := '1';
    SIGNAL rst                              : STD_LOGIC := '0';
    SIGNAL prog_full                        : STD_LOGIC := '0';
    SIGNAL prog_empty                       : STD_LOGIC := '1';
    SIGNAL rd_en                            : STD_LOGIC := '0';
    SIGNAL full                             : STD_LOGIC := '0';
    SIGNAL empty                            : STD_LOGIC := '1';
 
    signal dt_cntr_intg                     :  integer := 0;

    SIGNAL vmm_gbl_rst_sum_o                : STD_LOGIC := '0';
    SIGNAL vmm_configuring_sm               : STD_LOGIC := '0';
    SIGNAL vmm_gbl_rst_cntr                 : STD_LOGIC_VECTOR( 31 DOWNTO 0) := (OTHERS => '0');
    SIGNAL vmm_gbl_rst_pulse                : STD_LOGIC := '0';
    SIGNAL vmm_gbl_rst_pulse2               : STD_LOGIC := '0';


-----------===================================================================================----------------------

begin
		
		
--	--=============================--
U_init_config: process( reset, clk100)
--	--=============================--
begin
    if rising_edge( clk100) then 
        if (reset='1') then

            -- we can manually assign config data here
            -- currently we use the gui to load data
            
            for i in 0 to 50 loop
        	   regs_out( i) <= axi_reg( i+4);
            end loop;
        end if;
    end if;
end process U_init_config;


-- VMM config mux select

--	vmm_vmm_sel <= regs_out(63)(14 downto 12) ;

-- kjohns - we have to add the read in of the do bits later
-- commented out for now
-- the comparison of di and do is also commented out for now
-- and we need to add this back in later
	-- config in
--	process(vmm_clk_int_i, reset)
--	begin -- a load here will reset the 1616 bit word.
--		if (reset = '1') then
--			 vmm_cfg_in <= (others=>'1') ; -- in from VMM
--			 -- need 51 32 bit words for test value 
--		else
--			if falling_edge(vmm_clk_int_i) then -- we need to watch how the serial stream gets captured
--				if (vmm_rx_en_int = '1') then
--					-- if we send out LSB first
--					vmm_cfg_in <= cfg_bit_in & vmm_cfg_in(cfg_bits_max-1 downto 1) ; -- shift -> (only use top 1616)
--					-- if we send out MSB first
--					--- vmm_cfg_in <= vmm_cfg_in(cfg_bits_max-2 downto 0) & cfg_bit_in ; -- shift <- (only use low 1616)
--				end if ;
--			end if ;
--		end if ;
--	end process ;


-- map vmm cfg to reg_in registers
-- a continuous assignment
U_map_config: process( clk200, reset, vmm_cfg_in, cfg_sr_done, regs_in)
    begin
        if (reset = '1') then
            regs_in <= (others => (others => '0')) ;
        else
		    for i in 0 to 50 loop
                regs_in( i) <= vmm_cfg_in(	(((I+1)*32)-1) downto ( i*32));
            end loop;
		end if ;
end process U_map_config;




-- send out most significant bit
--	cfg_bit_out <= vmm_cfg_out(cfg_bits-1) ; -- send out bit 1616
	
	-- compare the two 1616 bit strings
--	comp_vectr : entity work.comp_vect
--	generic map(max_bits => cfg_bits) 
--	port map(A => vmm_cfg_out(cfg_bits-1 downto 0), -- tx stream. hi 16 unused
--				B => vmm_cfg_in(cfg_bits_max-1 downto 16), -- rx stream. low 16 unused -- changed to 17 by SAJONES, change back to 16
--				res => vect_eq -- 1=equal
--				) ;



--
-- ==================================================================== --
---------    System Reset, VMM Load, Global and Acquisition Reset
-- ==================================================================== --
--


config_vmm_fsm: process( vmm_clk_200)
-- cfg_sm_cntr is the state machine counter

    begin
	if rising_edge( vmm_clk_200) then
		if( reset = '1') then
			state <= s0 ;
			cfg_sm_cntr <= (others =>'0');   -- state machine time in state counter
            vmm_configuring_sm <= '0';       -- flag to activate the configuration IO switch
			gbl_rst <= '0' ;                 -- starts the vmm gbl_rst process
			vmm_run <= '0' ;                 -- starts the vmm configuration process
            reset_bcid_counter <= '0';
            acq_rst <= '0';                  -- acq rst
			vmm_ena_vmm_cfg_sm <= '0' ;      -- enable ENA            
        else	
            case state is
                when s0 => -- initialize and do the global reset
                    LEDxi <= b"000";
                    if( cfg_sm_cntr = x"00000000") then
                        gbl_rst <= '1' ;                        -- start the vmm gbl_rst process
                        vmm_configuring_sm <= '1';              -- activate the configuration IO switch
                        vmm_run <= '0' ;                        -- no vmm configuration process
                        acq_rst <= '0' ;                        -- no acq rst
			     	    vmm_ena_vmm_cfg_sm <= '0';              -- no enable ENA                          
                        reset_bcid_counter <= '0';              -- no bcid reset 
                        cfg_sm_cntr <= cfg_sm_cntr + '1';       -- incr counter
 
				    else 
				    
                        if( cfg_sm_cntr = x"00000040") then         -- at cfg_sm_cntr = 40, turn the global reset start off                              
                            gbl_rst <= '0' ;                        -- reset the vmm gbl_rst process starter
						    vmm_configuring_sm <= '1';              -- continue the configuration IO switch
                            cfg_sm_cntr <= cfg_sm_cntr + '1';       -- incr counter
                        else
                            if( cfg_sm_cntr = x"00100000") then     -- at cfg_cm_cntr = 100000, go to the next state and also reset the counter 
                                state <= s1 ; 
                                cfg_sm_cntr <= (others =>'0');
                                vmm_configuring_sm <= '1';          -- continue the configuration IO switch
                            else                                                                     
                                cfg_sm_cntr <= cfg_sm_cntr + '1';   -- otherwise, just increment the counter 
								vmm_configuring_sm <= '1';          -- continue the configuration IO switch
						    end if ;
                        end if ;
                    end if ;
                    
                --  the config state follows the same form as the global reset
                --  in this case vmm_run turns the config on
                --  and the same cfg_cm_cntr are used to turn it off and then wait to go
                --  to state s2
                when s1 => -- send the config bits
					LEDxi <= b"001";-- diagnostic
					if( cfg_sm_cntr = x"00000000") then
                        vmm_configuring_sm <= '1';                  -- continue the configuration IO switch
						vmm_run <= '1' ;                            -- start the vmm configuration process
                        cfg_sm_cntr <= cfg_sm_cntr + '1';           -- increment the counter 
					else 
						if( cfg_sm_cntr = x"00000040") then
                            vmm_configuring_sm <= '1';              -- continue the configuration IO switch
							vmm_run <= '0' ;                        -- reset the vmm configuration process start
							cfg_sm_cntr <= cfg_sm_cntr + '1';       -- increment the counter 
						else
							if( cfg_sm_cntr = x"00100000") then     -- give the configuration time to finish
								state <= s2 ; 
								vmm_configuring_sm <= '1';          -- continue the configuration IO switch
								cfg_sm_cntr <= (others =>'0');
							else
						      	cfg_sm_cntr <= cfg_sm_cntr + '1';
								vmm_configuring_sm <= '1';          -- continue the configuration IO switch
							end if ;
						end if ;
					end if ;
							
                -- and then we do the configuration again in the same way as in s1
			    when s2 => 
				    LEDxi <= b"010";
                    vmm_configuring_sm <= '1';   -- continue the configuration IO switch
					if( cfg_sm_cntr = x"00000000") then
						vmm_run <= '1' ; -- cfg run
						cfg_sm_cntr <= cfg_sm_cntr + '1';
					else 
						if( cfg_sm_cntr = x"00000040") then
							vmm_run <= '0' ; -- cfg run
							cfg_sm_cntr <= cfg_sm_cntr + '1';
						else
							if( cfg_sm_cntr = x"00100000") then
								state <= s3 ; 
								cfg_sm_cntr <= (others =>'0');
							else
								cfg_sm_cntr <= cfg_sm_cntr + '1';
							end if ;
						end if ;
					end if ;

                when s3 => -- now wait -- can probably delete this state
					LEDxi <= b"011";
                    vmm_configuring_sm <= '1';   -- continue the configuration IO switch
					if( cfg_sm_cntr = x"00010000") then
						state <= s4 ; 
						cfg_sm_cntr <= (others =>'0');
					else
						cfg_sm_cntr <= cfg_sm_cntr + '1';
					end if ;

                when s4 => -- do the acquisition reset
					LEDxi <= b"100"; 
					if( cfg_sm_cntr = x"00000000") then
                        vmm_configuring_sm <= '0';   --indicate in configuration sm sequence done
                        cfg_sm_cntr <= cfg_sm_cntr + '1';
                    else 
						vmm_configuring_sm <= '0';   --indicate configuration sm sequence done
                        if( cfg_sm_cntr = x"00000002") then
                            acq_rst <= '1' ; -- acq rst
							reset_bcid_counter <= '1';
                            cfg_sm_cntr <= cfg_sm_cntr + '1';
                        else 
                            if( cfg_sm_cntr = x"00000040") then
                                acq_rst <= '0' ; 
								reset_bcid_counter <= '0';
                                cfg_sm_cntr <= cfg_sm_cntr + '1';
                            else
                                if( cfg_sm_cntr = x"00100000") then
                                    state <= s5 ; 
                                    cfg_sm_cntr <= (others =>'0');
                                else
                                    cfg_sm_cntr <= cfg_sm_cntr + '1';
                                end if ;
                            end if ;
                        end if ;
                    end if ;

                when s5 => --  now set ena high - clear tk sync so can re-sync
                    LEDxi <= b"101";
					vmm_configuring_sm <= '0';   --indicate configuration sm sequence done
                    if( cfg_sm_cntr = x"00000400") then
						state <= s5; 
                        vmm_ena_vmm_cfg_sm <= '1' ; 
                    else
                        cfg_sm_cntr <= cfg_sm_cntr + '1';
                    end if ;
                when others => 
                    state <= s1 ;
                    vmm_run <= '0' ; -- cfg run
                    acq_rst <= '0' ; -- acq rst
                    vmm_ena_vmm_cfg_sm <= '0' ; -- enable ENA
                    cfg_sm_cntr <= (others =>'0');
                end case;
            end if;
		end if;
end process config_vmm_fsm ;

LEDx <= LEDxi;


-- map output reg to vmm cfg
-- this is really a continuous assignment....
vmmcfgout_gen:
for i in 0 to (cfg_bits_max/32)-1 generate -- 0 to 50 is 51x32=1632
	vmm_cfg_out( ((i*32)+32)-1 downto (i*32) ) <= regs_out(i) ;
end generate ;



----------------=======================================------------
--------------- vmm configuration shift register output------------
----------------=======================================------------


vmm_cfg_sr_inst: entity work.vmm_cfg_sr 
    generic map( cfg_bits => cfg_bits) -- for test use default of 32 not 1616
    port map(   
        clk                 => vmm_cktk, -- main clock
        rst                 => reset, -- reset
        load_en             => '0', -- vmm_load_en_pulse, -- load word to be sent
        run                 => vmm_run, -- start state machine cfg bit
        vmm_cfg_out         => vmm_cfg_out(cfg_bits-1 downto 0), -- only the low 1616 of 1632
        cfg_bit_out         => cfg_bit_out_i, -- serial out
        vmm_cktk_cfg_sr_en  => vmm_cktk_cfg_sr_en,
        vmm_ena             => vmm_ena_cfg_sr, -- or with cfg sm
        vmm_wen             => vmm_wen_cfg_sr, -- or with cfg sm
        statex              => statex,
        bit_cntrx           => bit_cntrx
    );



-- or together some control signals

vmm_gbl_rst_sum_o <=  gbl_rst or vmm_gbl_rst_pulse;
vmm_gbl_rst_sum <=  vmm_gbl_rst_sum_o;
vmm_configuring <= vmm_configuring_sm or vmm_gbl_rst_pulse2;



----------------=================================================------------
---------------- Generate secondary independent vmm global reset ------------
----------------=================================================------------


vmm_gbl_rst_pulse_sm: process( vmm_clk_200, reset, vmm_gbl_rst, vmm_gbl_rst_cntr, vmm_gbl_rst_pulse, vmm_gbl_rst_pulse2)
        begin
        if rising_edge( vmm_clk_200) then
            if( ( reset = '1') or ( vmm_gbl_rst = '0')) then
                vmm_gbl_rst_cntr <= (others =>'0');
                vmm_gbl_rst_pulse <= '0';
            else
                if( vmm_gbl_rst_cntr = x"00100000") then
                    vmm_gbl_rst_cntr <= x"00100000";
                    vmm_gbl_rst_pulse <= '0';
                    vmm_gbl_rst_pulse2 <= '0';
                else
                    if( vmm_gbl_rst_cntr = x"00000040") then
                        vmm_gbl_rst_cntr <= vmm_gbl_rst_cntr + '1';
                        vmm_gbl_rst_pulse <= '0';
                        vmm_gbl_rst_pulse2 <= '1';
                    else
                        if( vmm_gbl_rst_cntr = x"00000004") then
                            vmm_gbl_rst_cntr <= vmm_gbl_rst_cntr + '1';
                            vmm_gbl_rst_pulse <= '1';
                            vmm_gbl_rst_pulse2 <= '1';
                        else
                            if( vmm_gbl_rst_cntr = x"00000002") then
                                vmm_gbl_rst_cntr <= vmm_gbl_rst_cntr + '1';
                                vmm_gbl_rst_pulse <= '0';
                                vmm_gbl_rst_pulse2 <= '1';
                            else
                                vmm_gbl_rst_cntr <= vmm_gbl_rst_cntr + '1';
                            end if;                  
                        end if;
                    end if;
                end if;                  
            end if;
        end if;
end process vmm_gbl_rst_pulse_sm;              


----------------=======================================------------
---------------    vmm global and acquisition reset     -----------
----------------=======================================------------
      

vmm_cfg_rst_inst: entity work.vmm_cfg_rst
	port map(   
        clk            => vmm_clk_100, -- main clock
        rst            => reset, -- reset
        gbl_rst        => vmm_gbl_rst_sum_o, -- input
		acq_rst        => acq_rst, -- input
    	vmm_ena        => vmm_ena_cfg_rst, -- or with cfg sm
		vmm_wen        => vmm_wen_cfg_rst, -- or with cfg sm
		rst_state      => rst_state,
		cfg_rst_ctr_e  => cfg_rst_ctr,
		done           => vmm_rst_done -- pulse
	);			
				



----------------============================------------
---------------    VMM Data Acquisitions     -----------
----------------============================------------


GEN_DAQ : 
    for I in 0 to 7 generate
    begin
       	vmm_daq_inst : vmm_daq
            port map(
                vmm_clk_200              =>     vmm_clk_200, 
                reset                    =>      reset,
                vmmNumber                =>     std_logic_vector( to_unsigned( I, 3)),

                vmm_data0                =>     vmm_data0_vec( I),
                vmm_data1                =>     vmm_data1_vec( I),
                vmm_art                  =>     vmm_art_vec( I),
                turn_counter             =>     turn_counter, 
        
                vmm_cktk_daq_en          =>     vmm_cktk_daq_en_vec( I),
                vmm_ckdt_en              =>     vmm_ckdt_en_vec( I),
        
                vmm_ckdt                 =>     vmm_ckdt,
                vmm_ckart                =>     vmm_ckart,

                din                      =>     vmm_din_vec( I),
                dt_cntr_intg0            =>     dt_cntr_intg0_vec( I),
                dt_cntr_intg1            =>     dt_cntr_intg1_vec( I),
                vmm_data_buf             =>     vmm_data_buf_vec( I),

                rd_clk                   =>     vmm_clk_200,
                empty                    =>     vmm_empty( I),
                rd_data_count            =>     vmm_rd_data_count( I),
                wr_data_count            =>     vmm_wr_data_count( I),
                rd_en                    =>     vmm_rd_en( I),
                dout                     =>     vmm_dout_vec_i( I)
            );            
end generate GEN_DAQ;



----------------=======================================------------
---------------      VMM Round Robin Data Colection     -----------
----------------=======================================------------





-- pull data from daq (if available) in round robin style
U_Round_Robin: process( vmm_clk_200, reset, vmm_dout_vec_i, vmm_empty )

	begin

		if rising_edge( vmm_clk_200) then
			if( reset = '1') then

               vmm_rd_en <= (others => '0');
               wr_en <= '0';
			   rr_state  <= (others => '0');
                
			else
			   case rr_state is

		   	        when x"00" =>                    -- readout vmm#1 if data present and ro enabled
		   	              if( ( vmm_empty( 0) = '0') and ( vmm_ro( 0) = '1')) then
		   	                  vmm_rd_en( 0) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 0);
    		   	              rr_state <= x"01"; 
                          else
 		   	                  vmm_rd_en( 0) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"02"; 
		   	              end if; 

		   	        when x"01" =>                    -- continue readout vmm#1 if data present and ro enabled
		   	              if( ( vmm_empty( 0) = '0') and ( vmm_ro( 0) = '1')) then
		   	                  vmm_rd_en( 0) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 0);
       		   	              rr_state <= x"02"; 
                          else
                              vmm_rd_en( 0) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"02"; 
		   	              end if; 



		   	        when x"02" =>                    -- readout vmm#2 if data present and ro enabled
		   	              if( ( vmm_empty( 1) = '0') and ( vmm_ro( 1) = '1')) then
		   	                  vmm_rd_en( 1) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 1);
    		   	              rr_state <= x"03"; 
                          else
 		   	                  vmm_rd_en( 1) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"04"; 
		   	              end if; 

		   	        when x"03" =>                    -- continue readout vmm#2 if data present and ro enabled
		   	              if( ( vmm_empty( 1) = '0') and ( vmm_ro( 1) = '1')) then
		   	                  vmm_rd_en( 1) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 1);
       		   	              rr_state <= x"04"; 
                          else
                              vmm_rd_en( 1) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"04"; 
		   	              end if; 


						  
		   	        when x"04" =>                    -- readout vmm#3 if data present and ro enabled
		   	              if( ( vmm_empty( 2) = '0') and ( vmm_ro( 2) = '1')) then
		   	                  vmm_rd_en( 2) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 2);
    		   	              rr_state <= x"05"; 
                          else
 		   	                  vmm_rd_en( 2) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"06"; 
		   	              end if; 

		   	        when x"05" =>                    -- continue readout vmm#3 if data present and ro enabled
		   	              if( ( vmm_empty( 2) = '0') and ( vmm_ro( 2) = '1')) then
		   	                  vmm_rd_en( 2) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 2);
       		   	              rr_state <= x"06"; 
                          else
                              vmm_rd_en( 2) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"06"; 
		   	              end if; 



		   	        when x"06" =>                    -- readout vmm#4 if data present and ro enabled
		   	              if( ( vmm_empty( 3) = '0') and ( vmm_ro( 3) = '1')) then
		   	                  vmm_rd_en( 3) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 3);
    		   	              rr_state <= x"07"; 
                          else
 		   	                  vmm_rd_en( 3) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"08"; 
		   	              end if; 

		   	        when x"07" =>                    -- continue readout vmm#4 if data present and ro enabled
		   	              if( ( vmm_empty( 3) = '0') and ( vmm_ro( 3) = '1')) then
		   	                  vmm_rd_en( 3) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 3);
       		   	              rr_state <= x"08"; 
                          else
                              vmm_rd_en( 3) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"08"; 
		   	              end if; 
		   	              
		   	              
		   	              
		   	        when x"08" =>                    -- readout vmm#5 if data present and ro enabled
		   	              if( ( vmm_empty( 4) = '0') and ( vmm_ro( 4) = '1')) then
		   	                  vmm_rd_en( 4) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 4);
    		   	              rr_state <= x"09"; 
                          else
 		   	                  vmm_rd_en( 4) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"0a"; 
		   	              end if; 

		   	        when x"09" =>                    -- continue readout vmm#5 if data present and ro enabled
		   	              if( ( vmm_empty( 4) = '0') and ( vmm_ro( 4) = '1')) then
		   	                  vmm_rd_en( 4) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 4);
       		   	              rr_state <= x"0a"; 
                          else
                              vmm_rd_en( 4) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"0a"; 
		   	              end if; 



		   	        when x"0a" =>                    -- readout vmm#6 if data present and ro enabled
		   	              if( ( vmm_empty( 5) = '0') and ( vmm_ro( 5) = '1')) then
		   	                  vmm_rd_en( 5) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 5);
    		   	              rr_state <= x"0b"; 
                          else
 		   	                  vmm_rd_en( 5) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"0c"; 
		   	              end if; 

		   	        when x"0b" =>                    -- continue readout vmm#6 if data present and ro enabled
		   	              if( ( vmm_empty( 5) = '0') and ( vmm_ro( 5) = '1')) then
		   	                  vmm_rd_en( 5) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 5);
       		   	              rr_state <= x"0c"; 
                          else
                              vmm_rd_en( 5) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"0c"; 
		   	              end if; 



		   	        when x"0c" =>                    -- readout vmm#7 if data present and ro enabled
		   	              if( ( vmm_empty( 6) = '0') and ( vmm_ro( 6) = '1')) then
		   	                  vmm_rd_en( 6) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 6);
    		   	              rr_state <= x"0d"; 
                          else
 		   	                  vmm_rd_en( 6) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"0e"; 
		   	              end if; 

		   	        when x"0d" =>                    -- continue readout vmm#7 if data present and ro enabled
		   	              if( ( vmm_empty( 6) = '0')  and ( vmm_ro( 6) = '1')) then
		   	                  vmm_rd_en( 6) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 6);
       		   	              rr_state <= x"0e"; 
                          else
                              vmm_rd_en( 6) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"0e"; 
		   	              end if; 


		   	        when x"0e" =>                    -- readout vmm#8 if data present and ro enabled
		   	              if( ( vmm_empty( 7) = '0') and ( vmm_ro( 7) = '1')) then
		   	                  vmm_rd_en( 7) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 7);
    		   	              rr_state <= x"0f"; 
                          else
 		   	                  vmm_rd_en( 7) <= '0';
		   	                  wr_en <= '0';
       		   	              rr_state <= x"00"; 
		   	              end if; 

		   	        when x"0f" =>                    -- continue readout vmm#8 if data present and ro enabled
		   	              if( ( vmm_empty( 7) = '0') and ( vmm_ro( 7) = '1')) then
		   	                  vmm_rd_en( 7) <= '1';
		   	                  wr_en <= '1';
		   	                  din <= vmm_dout_vec_i( 7);
       		   	              rr_state <= x"00"; 
                          else
                              vmm_rd_en( 7) <= '0';
		   	                  wr_en <= '0';
                              rr_state <= x"00"; 
		   	              end if; 



                   when others => 
                         rr_state <= (others => '0');
                         vmm_rd_en <= (others => '0');
     	                 wr_en <= '0';
                        
                end case;
            end if;
        end if;
	end process U_Round_Robin;



--control output assignments
   vmm_ckart_en <= '1';
   vmm_cktp_en  <= '1';
   vmm_ckbc_en  <= '1';

--clock input assignments
    vmm_ckart_i <= vmm_ckart;
  
--data input assignments
    cfg_bit_in_i <= cfg_bit_in;
    testX_i      <= testX;
	
-- data output assignments
	cfg_bit_out <= cfg_bit_out_i;
    vmm_dout_vec <= vmm_dout_vec_i;
  

fifo_round_robin_inst: fifo_round_robin
  PORT MAP (
    rst             => reset,
    wr_clk                      => vmm_clk_200,
    rd_clk                      => vmm_clk_200,
    din             => din,
    wr_en           => wr_en,
    rd_en                       => rr_data_fifo_rd_en,
    dout                        => rr_data_fifo_dout,
    full            => open,
    almost_full     => open,

    empty                       => rr_data_fifo_empty,

    rd_data_count               => rr_rd_data_count,
    wr_data_count               => rr_wr_data_count,
    almost_empty    => open
  );
  
end rtl;
