package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentElute extends Component
	{
		// Constructor
		public function ComponentElute(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorDescription():String
		{
			return super.flash_proxy::getProperty("reactordescription");
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
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
		
		public function get EluteReagentDescription():String
		{
			return super.flash_proxy::getProperty("reagentdescription");
		}
		
		public function get EluteReagentValidation():String
		{
			return super.flash_proxy::getProperty("reagentvalidation");
		}

		public function get EluteTarget():Reagent
		{
			if (m_pTarget == null)
			{
				m_pTarget = new Reagent(null, super.flash_proxy::getProperty("target"));
			}
			return m_pTarget;
		}
		public function set EluteTarget(value:Reagent):void
		{
			super.flash_proxy::setProperty("target", value);
			m_pTarget = null;
		}
		
		public function get EluteTargetDescription():String
		{
			return super.flash_proxy::getProperty("targetdescription");
		}
		
		public function get EluteTargetValidation():String
		{
			return super.flash_proxy::getProperty("targetvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sEluteDetails:String = JSONDataObject("reactor", Reactor);
			sEluteDetails += JSONDataObject("reagent", EluteReagent.ReagentID);
			sEluteDetails += JSONDataObject("target", EluteTarget.ReagentID, false);
			return sEluteDetails;
		}

		// Type
		static public var TYPE:String = "ELUTE";

		// State components
		private var m_pReagent:Reagent;
		private var m_pTarget:Reagent;

		// Default format
		private var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"ELUTE\"," +
			"\"id\":0," +
			"\"name\":\"\"," +
			"\"reactor\":0," +
			"\"reagent\":" + Reagent.DEFAULT + "," +
			"\"target\":" + Reagent.DEFAULT + "}";
	}
}
