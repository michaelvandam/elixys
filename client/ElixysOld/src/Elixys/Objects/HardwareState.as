package Elixys.Objects
{
	
	import flash.utils.flash_proxy;
	
	public class HardwareState extends JSONObject
	{
		// Constructor
		public function HardwareState(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Cooling():Boolean
		{
			return super.flash_proxy::getProperty("cooling");
		}
		public function Vacuum():Number
		{
			return super.flash_proxy::getProperty("vacuum");
		}
		public function PressureRegulators():Array
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
		public function ReagentRobot():ReagentRobotState
		{
			// Parse the robot state
			if (m_pReagentRobot == null)
			{
				m_pReagentRobot = new ReagentRobotState(null, super.flash_proxy::getProperty("reagentrobot"));
			}
			return m_pReagentRobot;
		}
		public function Reactors():Array
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

		// Type
		static public var TYPE:String = "hardwarestate";
		
		// State components
		private var m_pPressureRegulators:Array = null;
		private var m_pReagentRobot:ReagentRobotState = null;
		private var m_pReactors:Array = null;
	}
}
