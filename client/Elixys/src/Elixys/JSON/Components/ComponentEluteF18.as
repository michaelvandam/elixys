package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	import Elixys.JSON.State.Reagent;
	
	import flash.utils.flash_proxy;
	
	public class ComponentEluteF18 extends ComponentBase
	{
		// Constructor
		public function ComponentEluteF18(data:String = null, existingcontent:Object = null)
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
			return "ELUTEF18";
		}
		public static function get SKINUP():Class
		{
			return tools_elute_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_elute_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_elute_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_elute_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 3;
		public static var FIELDLABELS:Array = [
			"REAGENT", 
			"DURATION", 
			"PRESSURE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"SECONDS", 
			"PSI"
		];
		public static var FIELDPROPERTIES:Array = [
			"EluteReagent", 
			"EluteTime", 
			"ElutePressure"
		];
		
		// Data wrappers
		public function get EluteTime():uint
		{
			return super.flash_proxy::getProperty("elutetime");
		}
		public function set EluteTime(value:uint):void
		{
			super.flash_proxy::setProperty("elutetime", value);
		}
		
		public function get EluteTimeValidation():String
		{
			return super.flash_proxy::getProperty("elutetimevalidation");
		}
		
		public function get ElutePressure():uint
		{
			return super.flash_proxy::getProperty("elutepressure");
		}
		public function set ElutePressure(value:uint):void
		{
			super.flash_proxy::setProperty("elutepressure", value);
		}
		
		public function get ElutePressureValidation():String
		{
			return super.flash_proxy::getProperty("elutepressurevalidation");
		}

		public function get EluteReagent():Reagent
		{
			if (m_pReagent == null)
			{
				m_pReagent = new Reagent(null, super.flash_proxy::getProperty("reagent"));
			}
			return m_pReagent;
		}
		public function set EluteReagent(value:Reagent):void
		{
			super.flash_proxy::setProperty("reagent", value);
			m_pReagent = null;
		}
		
		public function get EluteReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sEluteF18Details:String = JSONDataObject("elutetime", EluteTime);
			sEluteF18Details += JSONDataObject("elutepressure", ElutePressure);
			sEluteF18Details += JSONDataObject("reagent", EluteReagent.ReagentID, false);
			return sEluteF18Details;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentEluteF18A:ComponentEluteF18 = new ComponentEluteF18(null, pComponentA);
			var pComponentEluteF18B:ComponentEluteF18 = new ComponentEluteF18(null, pComponentB);
			if (pComponentEluteF18A.EluteTime != pComponentEluteF18B.EluteTime)
			{
				return false;
			}
			if (pComponentEluteF18A.ElutePressure != pComponentEluteF18B.ElutePressure)
			{
				return false;
			}
			return Reagent.CompareReagents(pComponentEluteF18A.EluteReagent, pComponentEluteF18B.EluteReagent);
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sEluteTimeError = ValidateField(EluteTime, EluteTimeValidation);
			m_sElutePressureError = ValidateField(ElutePressure, ElutePressureValidation);
			m_sEluteReagentError = ValidateField(EluteReagent, EluteReagentError);
		}
		
		// Validation fields
		public function get EluteTimeError():String
		{
			return m_sEluteTimeError;
		}
		public function get ElutePressureError():String
		{
			return m_sElutePressureError;
		}
		public function get EluteReagentError():String
		{
			return m_sEluteReagentError;
		}
		
		// State components
		private var m_pReagent:Reagent;

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ELUTEF18\"," +
			"\"id\":0," +
			"\"name\":\"Elute F18\"," +
			"\"elutetime\":0," +
			"\"elutepressure\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "}";
		
		// Validation errors
		protected var m_sEluteTimeError:String = "";
		protected var m_sElutePressureError:String = "";
		protected var m_sEluteReagentError:String = "";
	}
}
