--Copyright 1986-2014 Xilinx, Inc. All Rights Reserved.
----------------------------------------------------------------------------------
--Tool Version: Vivado v.2014.4.1 (win64) Build 1149489 Thu Feb 19 16:23:09 MST 2015
--Date        : Wed Mar 11 13:50:06 2015
--Host        : lithe-ad-work running 64-bit Service Pack 1  (build 7601)
--Command     : generate_target mbsys_wrapper.bd
--Design      : mbsys_wrapper
--Purpose     : IP block netlist
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.all;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
use work.vmm_pkg.all;

entity scope_select is
    port (

    scopeD0          : out std_logic;
    scopeD1          : out std_logic;
    scopeD2          : out std_logic;
    scopeD3          : out std_logic;
    scopeD4          : out std_logic;
    scopeD5          : out std_logic;
    scopeD6          : out std_logic;
    scopeD7          : out std_logic;
  
    scope_CE         : out std_logic_vector ( 7 downto 0) := (others=>'1');
    vmm_2display     : in  std_logic_vector( 4 downto 0) := (others=>'0');


    vmm_ckbc            : in std_logic;
    vmm_ckbc_en         : in std_logic;

    vmm_cktp            : in std_logic;
    vmm_cktp_en         : in std_logic;

    vmm_di              : in std_logic;
    vmm_di_en_vec       : in std_logic_vector ( 7 downto 0) := (others=>'1');
    
    vmm_data0_vec       : in std_logic_vector ( 7 downto 0) := (others=>'1');
    vmm_data1_vec       : in std_logic_vector ( 7 downto 0) := (others=>'1');

    vmm_do_vec          : in std_logic_vector ( 7 downto 0) := (others=>'1');
    vmm_wen_vec         : in std_logic_vector ( 7 downto 0) := (others=>'1');
    vmm_ena_vec         : in std_logic_vector ( 7 downto 0) := (others=>'1');

    vmm_ckart           : in std_logic;
    vmm_art_vec         : in std_logic_vector ( 7 downto 0) := (others=>'1');

    vmm_cktk            : in std_logic;
    vmm_cktk_en_vec     : in std_logic_vector ( 7 downto 0) := (others=>'1');

    vmm_ckdt            : in std_logic;
    vmm_ckdt_en_vec     : in std_logic_vector ( 7 downto 0) := (others=>'1');

    ext_trigger_in        : in std_logic;
    ext_trigger_deb       : in std_logic;
    ext_trigger_pulse     : in std_logic;
    busy_from_ext_trigger : in std_logic;

    vmm_cfg_en_vec        : in std_logic_vector ( 7 downto 0) := (others=>'1');
    vmm_gbl_rst           : in std_logic := '0';
    vmm_gbl_rst_sum       : in STD_LOGIC := '0';

    reset                   : in std_logic;
    reset_old               : in std_logic;
    reset_new               : in std_logic;
    vmm_load                : in std_logic;
    
    rst_state               : in std_logic_vector( 2 downto 0);
    vmm_configuring         : in std_logic;
    int_trig                : in std_logic;
    cktp_done               : in std_logic;
    
    LEDx                    : in std_logic_vector( 2 downto 0);
    vmm_ena_vmm_cfg_sm      : in std_logic;
    acq_rst_from_vmm_fsm    : in std_logic;
    vmm_ena_vmm_cfg_sm_vec  : in std_logic_vector( 7 downto 0);

    acq_rst_from_data0      : in std_logic_vector( 7 downto 0);
    vmm_acq_rst_running     : in std_logic_vector( 7 downto 0);
    acq_rst_term_count      : in std_logic_vector( 31 downto 0);
    
    dt_state                : in array_8x4bit;
    acq_rst_counter         : in array_8x32bit

    );
end scope_select;

architecture STRUCTURE of scope_select is

--  signal vmm_2display : std_logic_vector( 4 downto 0) := (others=>'0');

begin
                                            
-- select display choice
process ( vmm_2display, vmm_ckbc, vmm_ckbc_en, vmm_di, 
    vmm_di_en_vec, vmm_cktk_en_vec, vmm_ckdt_en_vec, vmm_ckdt,
    vmm_wen_vec, vmm_ena_vec, vmm_do_vec, vmm_cktk, vmm_cktp, vmm_cktp_en, 
    vmm_data0_vec, vmm_data1_vec, vmm_ckart, vmm_art_vec,
    ext_trigger_in, ext_trigger_deb, ext_trigger_pulse, busy_from_ext_trigger,
    vmm_cfg_en_vec, vmm_gbl_rst, reset, reset_old, reset_new, vmm_load, rst_state, vmm_configuring,
    int_trig, cktp_done, LEDx, vmm_ena_vmm_cfg_sm, acq_rst_from_vmm_fsm, vmm_ena_vmm_cfg_sm_vec,
    acq_rst_from_data0, vmm_acq_rst_running, acq_rst_term_count, dt_state, acq_rst_counter    
    )

        begin
            case vmm_2display is
--0x00                                        
--vmm0 cfg                        
               when "00000" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 0); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 0);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 0);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 0);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 0);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 0);
     
--0x01
--vmm0 data                        
               when "00001" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_data1_vec( 0);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 0);
                         scope_CE( 3) <= '1';                     
                         scopeD4 <= vmm_ckdt;
                         scope_CE( 4) <= vmm_ckdt_en_vec( 0);                     
                         scopeD5 <= vmm_ckart;
                         scope_CE( 5) <= '1';  
                         scopeD6 <= vmm_art_vec( 0);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk;
                         scope_CE( 7) <= vmm_cktk_en_vec( 0);

--0x02
--vmm1 cfg                        
               when "00010" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_di;
                        scope_CE( 1) <= vmm_di_en_vec( 1); 
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 1);
                        scope_CE( 3) <= '1';
                        scopeD4 <= vmm_do_vec( 1);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_wen_vec( 1);
                        scope_CE( 5) <= '1';
                        scopeD6 <= vmm_ena_vec( 1);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk ;
                        scope_CE( 7) <= vmm_cktk_en_vec( 1);

                   
--0x03
--vmm1 data                        
               when "00011" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_data1_vec( 1);
                        scope_CE( 1) <= '1';       
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 1);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_ckdt;
                        scope_CE( 4) <= vmm_ckdt_en_vec( 1);                     
                        scopeD5 <= vmm_ckart;
                        scope_CE( 5) <= '1';  
                        scopeD6 <= vmm_art_vec( 1);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk;
                        scope_CE( 7) <= vmm_cktk_en_vec( 1);

                 
--0x04
--vmm2 cfg                        
               when "00100" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_di;
                        scope_CE( 1) <= vmm_di_en_vec( 2); 
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 2);
                        scope_CE( 3) <= '1';
                        scopeD4 <= vmm_do_vec( 2);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_wen_vec( 2);
                        scope_CE( 5) <= '1';
                        scopeD6 <= vmm_ena_vec( 2);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk ;
                        scope_CE( 7) <= vmm_cktk_en_vec( 2);
    
                       
--0x05
--vmm2 data                        
               when "00101" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_data1_vec( 2);
                        scope_CE( 1) <= '1';       
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 2);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_ckdt;
                        scope_CE( 4) <= vmm_ckdt_en_vec( 2);                     
                        scopeD5 <= vmm_ckart;
                        scope_CE( 5) <= '1';  
                        scopeD6 <= vmm_art_vec( 2);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk;
                        scope_CE( 7) <= vmm_cktk_en_vec( 2);
                           
                                      
--0x06
--vmm3 cfg                        
               when "00110" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_di;
                        scope_CE( 1) <= vmm_di_en_vec( 3); 
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 3);
                        scope_CE( 3) <= '1';
                        scopeD4 <= vmm_do_vec( 3);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_wen_vec( 3);
                        scope_CE( 5) <= '1';
                        scopeD6 <= vmm_ena_vec( 3);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk ;
                        scope_CE( 7) <= vmm_cktk_en_vec( 3);
    
                       
--0x07
--vmm3 data                        
               when "00111" => 
                        scopeD0 <= vmm_ckbc;
                        scope_CE( 0) <= vmm_ckbc_en;                     
                        scopeD1 <= vmm_data1_vec( 3);
                        scope_CE( 1) <= '1';       
                        scopeD2 <= vmm_cktp;
                        scope_CE( 2) <= vmm_cktp_en;                     
                        scopeD3 <= vmm_data0_vec( 3);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_ckdt;
                        scope_CE( 4) <= vmm_ckdt_en_vec( 3);                     
                        scopeD5 <= vmm_ckart;
                        scope_CE( 5) <= '1';  
                        scopeD6 <= vmm_art_vec( 3);
                        scope_CE( 6) <= '1';  
                        scopeD7 <= vmm_cktk;
                        scope_CE( 7) <= vmm_cktk_en_vec( 3);
    
--0x08
--vmm4 cfg                        
                when "01000" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 4); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 4);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 4);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 4);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 4);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 4);
     
                        
--0x09
--vmm4 data                        
               when "01001" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_data1_vec( 4);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 4);
                         scope_CE( 3) <= '1';                     
                         scopeD4 <= vmm_ckdt;
                         scope_CE( 4) <= vmm_ckdt_en_vec( 4);                     
                         scopeD5 <= vmm_ckart;
                         scope_CE( 5) <= '1';  
                         scopeD6 <= vmm_art_vec( 4);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk;
                         scope_CE( 7) <= vmm_cktk_en_vec( 4);


--0x0A
--vmm5 cfg                        
                when "01010" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 5); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 5);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 5);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 5);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 5);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 5);
     
                        
--0x0B
--vmm5 data                        
                when "01011" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_data1_vec( 5);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 5);
                         scope_CE( 3) <= '1';                     
                         scopeD4 <= vmm_ckdt;
                         scope_CE( 4) <= vmm_ckdt_en_vec( 5);                     
                         scopeD5 <= vmm_ckart;
                         scope_CE( 5) <= '1';  
                         scopeD6 <= vmm_art_vec( 5);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk;
                         scope_CE( 7) <= vmm_cktk_en_vec( 5);


--0x0C
--vmm6 cfg                        
                when "01100" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 6); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 6);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 6);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 6);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 6);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 6);
     
--0x0D                       
--vmm6 data                        
                when "01101" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_data1_vec( 6);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 6);
                         scope_CE( 3) <= '1';                     
                         scopeD4 <= vmm_ckdt;
                         scope_CE( 4) <= vmm_ckdt_en_vec( 6);                     
                         scopeD5 <= vmm_ckart;
                         scope_CE( 5) <= '1';  
                         scopeD6 <= vmm_art_vec( 6);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk;
                         scope_CE( 7) <= vmm_cktk_en_vec( 6);

--0x0E
--vmm7 cfg                        
                when "01110" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 7); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 7);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 7);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 7);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 7);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 7);

--0x0F
--vmm7 data                        
                when "01111" => 
                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_data1_vec( 7);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 7);
                         scope_CE( 3) <= '1';                     
                         scopeD4 <= vmm_ckdt;
                         scope_CE( 4) <= vmm_ckdt_en_vec( 7);                     
                         scopeD5 <= vmm_ckart;
                         scope_CE( 5) <= '1';  
                         scopeD6 <= vmm_art_vec( 7);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk;
                         scope_CE( 7) <= vmm_cktk_en_vec( 7);

--data0 --0x10
               when "10000" => 
                        scopeD0 <= vmm_data0_vec( 0);
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= vmm_data0_vec( 1);
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= vmm_data0_vec( 2);
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= vmm_data0_vec( 3);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_data0_vec( 4);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_data0_vec( 5);
                        scope_CE( 5) <= '1';                     
                        scopeD6 <= vmm_data0_vec( 6);
                        scope_CE( 6) <= '1';                     
                        scopeD7 <= vmm_data0_vec( 7);
                        scope_CE( 7) <= '1';                     


--data1 --0x11
               when "10001" => 
                        scopeD0 <= vmm_data1_vec( 0);
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= vmm_data1_vec( 1);
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= vmm_data1_vec( 2);
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= vmm_data1_vec( 3);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_data1_vec( 4);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_data1_vec( 5);
                        scope_CE( 5) <= '1';                     
                        scopeD6 <= vmm_data1_vec( 6);
                        scope_CE( 6) <= '1';                     
                        scopeD7 <= vmm_data1_vec( 7);
                        scope_CE( 7) <= '1';                     


-- art --0x12
               when "10010" => 
                        scopeD0 <= vmm_art_vec( 0);
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= vmm_art_vec( 1);
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= vmm_art_vec( 2);
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= vmm_art_vec( 3);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_art_vec( 4);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_art_vec( 5);
                        scope_CE( 5) <= '1';                     
                        scopeD6 <= vmm_art_vec( 6);
                        scope_CE( 6) <= '1';                     
                        scopeD7 <= vmm_art_vec( 7);
                        scope_CE( 7) <= '1';                     


--ext trigger --0x13
               when "10011" => 
                        scopeD0 <= ext_trigger_in;
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= ext_trigger_deb;
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= ext_trigger_pulse;
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= busy_from_ext_trigger;
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_data0_vec( 1);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_ckdt_en_vec( 1);
                        scope_CE( 5) <= '1';  
                        scopeD6 <= vmm_cktk;
                        scope_CE( 6) <= vmm_cktk_en_vec( 1);  
                        scopeD7 <= vmm_di_en_vec( 1);
                        scope_CE( 7) <= '1';                     


--int trigger --0x14
               when "10100" => 
                        scopeD0 <= busy_from_ext_trigger;
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= vmm_gbl_rst;
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= reset;
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= int_trig;
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= cktp_done;
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_cktp;
                        scope_CE( 5) <= vmm_cktp_en;  
--                        scopeD6 <= reset_old;
                        scopeD6 <= vmm_load;
                        scope_CE( 6) <= '1';  
                        scopeD7 <= reset_new;
                        scope_CE( 7) <= '1';                     


--configure --0x15
               when "10101" => 

                         scopeD0 <= vmm_ckbc;
                         scope_CE( 0) <= vmm_ckbc_en;                     
                         scopeD1 <= vmm_di;
                         scope_CE( 1) <= vmm_di_en_vec( 0); 
                         scopeD2 <= vmm_cktp;
                         scope_CE( 2) <= vmm_cktp_en;                     
                         scopeD3 <= vmm_data0_vec( 0);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_do_vec( 0);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= vmm_wen_vec( 0);
                         scope_CE( 5) <= '1';
                         scopeD6 <= vmm_ena_vec( 0);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= vmm_cktk ;
                         scope_CE( 7) <= vmm_cktk_en_vec( 0);

--gbl_rst --0x16
               when "10110" => 

                         scopeD0 <= vmm_gbl_rst_sum;
                         scope_CE( 0) <= '1';                     
                         scopeD1 <= rst_state( 0);
                         scope_CE( 1) <= '1'; 
                         scopeD2 <= rst_state( 1);
                         scope_CE( 2) <= '1';                     
                         scopeD3 <= rst_state( 2);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_configuring;
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= LEDx( 0);
                         scope_CE( 5) <= '1';
                         scopeD6 <= LEDx( 1);
                         scope_CE( 6) <= '1';  
--                         scopeD7 <= LEDx( 2);
                         scopeD7 <= LEDx( 2);
                         scope_CE( 7) <= '1';

--config control --0x17
               when "10111" => 
                            -- acq_rst_from_vmm_fsm momentary over vmm_ena_vmm_cfg_sm   vmm_ena_vmm_cfg_sm_vec( I)
                         scopeD0 <= vmm_ena_vmm_cfg_sm;
                         scope_CE( 0) <= '1';                     
                         scopeD1 <= acq_rst_from_vmm_fsm;
                         scope_CE( 1) <= '1'; 
                         scopeD2 <= vmm_ena_vmm_cfg_sm_vec( 1);
                         scope_CE( 2) <= '1';                     
                         scopeD3 <= rst_state( 2);
                         scope_CE( 3) <= '1';
                         scopeD4 <= vmm_configuring;
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= LEDx( 0);
                         scope_CE( 5) <= '1';
                         scopeD6 <= LEDx( 1);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= LEDx( 2);
                         scope_CE( 7) <= '1';


--acq reset --0x18
               when "11000" => 
                         scopeD0 <= vmm_data0_vec( 0);
                         scope_CE( 0) <= '1';       
                         scopeD1 <= vmm_data1_vec( 0);
                         scope_CE( 1) <= '1';       
                         scopeD2 <= vmm_cktk;
                         scope_CE( 2) <= vmm_cktk_en_vec( 0);
                         scopeD3 <= acq_rst_from_data0( 0);
                         scope_CE( 3) <= '1';       
                         scopeD4 <= vmm_acq_rst_running( 0);
                         scope_CE( 4) <= '1';                     
                         scopeD5 <= acq_rst_term_count( 0);
                         scope_CE( 5) <= '1';
                         scopeD6 <= dt_state( 0)( 0);
                         scope_CE( 6) <= '1';  
                         scopeD7 <= dt_state( 0)( 1);
                         scope_CE( 7) <= '1';

--acq reset ctrs--0x19
               when "11001" => 
                         scopeD0 <= dt_state( 0)( 0);
                         scope_CE( 0) <= '1';
                         scopeD1 <= dt_state( 0)( 1);
                         scope_CE( 1) <= '1';
                         scopeD2 <= dt_state( 0)( 2);
                         scope_CE( 2) <= '1';
                         scopeD3 <= dt_state( 0)( 3);
                         scope_CE( 3) <= '1';  
                         scopeD0 <= dt_state( 0)( 0);
                         scope_CE( 0) <= '1';

 
    
                    when others =>  
                        scopeD0 <= vmm_data0_vec( 0);
                        scope_CE( 0) <= '1';                     
                        scopeD1 <= vmm_data0_vec( 1);
                        scope_CE( 1) <= '1';                     
                        scopeD2 <= vmm_data0_vec( 2);
                        scope_CE( 2) <= '1';                     
                        scopeD3 <= vmm_data0_vec( 3);
                        scope_CE( 3) <= '1';                     
                        scopeD4 <= vmm_data0_vec( 4);
                        scope_CE( 4) <= '1';                     
                        scopeD5 <= vmm_data0_vec( 5);
                        scope_CE( 5) <= '1';                     
                        scopeD6 <= vmm_data0_vec( 6);
                        scope_CE( 6) <= '1';                     
                        scopeD7 <= vmm_data0_vec( 7);
                        scope_CE( 7) <= '1';                     
               
            end case;
       end process;
    	
  

    
end STRUCTURE;




