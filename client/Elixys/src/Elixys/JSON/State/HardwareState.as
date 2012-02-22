package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class HardwareState extends JSONObject
	{
		// Constructor
		public function HardwareState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "hardwarestate";
		}

		// Data wrappers
		public function get Cooling():Boolean
		{
			return super.flash_proxy::getProperty("cooling");
		}
		public function get Vacuum():Elixys.JSON.State.VacuumState
		{
			// Parse the vacuum state
			if (m_pVacuumState == null)
			{
				m_pVacuumState = new VacuumState(null, super.flash_proxy::getProperty("vacuum"));
			}
			return m_pVacuumState;
		}
		public function get LiquidSensors():Array
		{
			// Parse the liquid sensors
			if (m_pLiquidSensors == null)
			{
				m_pLiquidSensors = new Array();
				var pLiquidSensors:Array = super.flash_proxy::getProperty("liquidsensors");
				for each (var pLiquidSensorObject:Object in pLiquidSensors)
				{
					var pLiquidSensor:LiquidSensorState = new LiquidSensorState(null, pLiquidSensorObject);
					m_pLiquidSensors.push(pLiquidSensor);
				}
			}
			return m_pLiquidSensors;
		}
		public function get PressureRegulators():Array
		{
			// Parse the pressure regulators
			if (m_pPressureRegulators == null)
			{
				m_pPressureRegulators = new Array();
				var pPressureRegulators:Array = super.flash_proxy::getProperty("pressureregulators");
				for each (var pPressureRegulatorObject:Object in pPressureRegulators)
				{
					var pPressureRegulator:PressureRegulatorState = new PressureRegulatorState(null, pPressureRegulatorObject);
					m_pPressureRegulators.push(pPressureRegulator);
				}
			}
			return m_pPressureRegulators;
		}
		public function get Valves():Array
		{
			// Parse the valves
			if (m_pValves == null)
			{
				m_pValves = new Array();
				var pValves:Array = super.flash_proxy::getProperty("valves");
				for each (var pValveObject:Object in pValves)
				{
					var pValve:ValveState = new ValveState(null, pValveObject);
					m_pValves.push(pValve);
				}
			}
			return m_pValves;
		}
		public function get ReagentRobot():ReagentRobotState
		{
			// Parse the robot state
			if (m_pReagentRobot == null)
			{
				m_pReagentRobot = new ReagentRobotState(null, super.flash_proxy::getProperty("reagentrobot"));
			}
			return m_pReagentRobot;
		}
		public function get Reactors():Array
		{
			// Parse the reactors
			if (m_pReactors == null)
			{
				m_pReactors = new Array();
				var pReactors:Array = super.flash_proxy::getProperty("reactors");
				for each (var pReactorObject:Object in pReactors)
				{
					var pReactor:ReactorState = new ReactorState(null, pReactorObject);
					m_pReactors.push(pReactor);
				}
			}
			return m_pReactors;
		}

		// State components
		private var m_pVacuumState:VacuumState;
		private var m_pLiquidSensors:Array;
		private var m_pPressureRegulators:Array;
		private var m_pValves:Array;
		private var m_pReagentRobot:ReagentRobotState;
		private var m_pReactors:Array;
	}
}
