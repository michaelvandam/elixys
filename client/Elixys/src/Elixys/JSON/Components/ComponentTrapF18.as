package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentTrapF18 extends ComponentBase
	{
		// Constructor
		public function ComponentTrapF18(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "TRAPF18";
		}
		public static function get SKINUP():Class
		{
			return tools_trap_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_trap_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_trap_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_trap_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 3;
		public static var FIELDLABELS:Array = [
			"CYCLOTRON PUSH", 
			"DURATION", 
			"PRESSURE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_CHECKBOX,
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"SECONDS", 
			"PSI"
		];
		public static var FIELDPROPERTIES:Array = [
			"CyclotronFlag", 
			"TrapTime", 
			"TrapPressure"
		];
		
		// Data wrappers
		public function get CyclotronFlag():uint
		{
			return super.flash_proxy::getProperty("cyclotronflag");
		}
		public function set CyclotronFlag(value:uint):void
		{
			super.flash_proxy::setProperty("cyclotronflag", value);
		}
		
		public function get CyclotronFlagValidation():String
		{
			return super.flash_proxy::getProperty("cyclotronflagvalidation");
		}
		
		public function get TrapTime():uint
		{
			return super.flash_proxy::getProperty("traptime");
		}
		public function set TrapTime(value:uint):void
		{
			super.flash_proxy::setProperty("traptime", value);
		}
		
		public function get TrapTimeValidation():String
		{
			return super.flash_proxy::getProperty("traptimevalidation");
		}

		public function get TrapPressure():uint
		{
			return super.flash_proxy::getProperty("trappressure");
		}
		public function set TrapPressure(value:uint):void
		{
			super.flash_proxy::setProperty("trappressure", value);
		}
		
		public function get TrapPressureValidation():String
		{
			return super.flash_proxy::getProperty("trappressurevalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sTrapF18Details:String = JSONDataObject("cyclotronflag", CyclotronFlag);
			sTrapF18Details += JSONDataObject("traptime", TrapTime);
			sTrapF18Details += JSONDataObject("trappressure", TrapPressure, false);
			return sTrapF18Details;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentTrapF18A:ComponentTrapF18 = new ComponentTrapF18(null, pComponentA);
			var pComponentTrapF18B:ComponentTrapF18 = new ComponentTrapF18(null, pComponentB);
			if (pComponentTrapF18A.CyclotronFlag != pComponentTrapF18B.CyclotronFlag)
			{
				return false;
			}
			if (pComponentTrapF18A.TrapTime != pComponentTrapF18B.TrapTime)
			{
				return false;
			}
			if (pComponentTrapF18A.TrapPressure != pComponentTrapF18B.TrapPressure)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sCyclotronFlagError = ValidateField(CyclotronFlag, CyclotronFlagValidation);
			m_sTrapTimeError = ValidateField(TrapTime, TrapTimeValidation);
			m_sTrapPressureError = ValidateField(TrapPressure, TrapPressureValidation);
		}
		
		// Validation fields
		public function get CyclotronFlagError():String
		{
			return m_sCyclotronFlagError;
		}
		public function get TrapTimeError():String
		{
			return m_sTrapTimeError;
		}
		public function get TrapPressureError():String
		{
			return m_sTrapPressureError;
		}
				
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"TRAPF18\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"cyclotronflag\":0," +
			"\"traptime\":0," +
			"\"trappressure\":0}";
		
		// Validation errors
		protected var m_sCyclotronFlagError:String = "";
		protected var m_sTrapTimeError:String = "";
		protected var m_sTrapPressureError:String = "";
	}
}
